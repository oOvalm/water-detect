import json
import logging
import os
import subprocess
import time
from datetime import datetime
import cv2

from common.db_model import FileType, FileExtra, AnalyseFileType, FileStatus
from common_service import redisService
from common_service.fileService import FileManager
from common_service.lock import RedisLock
from common_service.redisService import GetDefaultRedis
from common.video_utils import InitStreamOutput, WriteFrameAsStream, merge_video_files
from database.models import FileInfo, StreamKeyInfo
from waterDetect import settings
from yolo.yolo_model.analyse import GetFromModel

rtmp_host = f"{settings.NGINX_CONFIG['host']}:{settings.NGINX_CONFIG['rtmp_port']}"

TempVideoFolder = os.path.join(settings.MEDIA_ROOT, 'tmp')
log = logging.getLogger(__name__)
def AnalyseFrame(frame):
    # 处理成黑白
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray
    # return AnalyseImage(frame)


def save_frameList(frames, outputPath, fps):
    if len(frames) == 0:
        return
    height, width, _ = frames[0].shape
    # 定义视频编码器和输出文件名
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # 创建视频写入对象
    out = cv2.VideoWriter(outputPath, fourcc, fps, (width, height))

    # 将帧列表中的帧写入视频文件
    for f in frames:
        out.write(f)

    # 释放视频写入对象
    out.release()


def capture_streamNanalyse(app, stream_key, event, que):
    # ctx 用于存此次分析的上下文
    # process 输入流进程
    process, ctx = None, {}
    stream_name = f"{app}_{stream_key}"
    try:
        log.info(f"start capture {stream_name}")
        # 抢流的监听锁
        with RedisLock(GetDefaultRedis(), f"capture_ori_stream:{stream_name}", expire=5) as r:
            # 拿不到锁直接返回
            if not r.is_acquired:
                print('get lock fail')
                m3u8Path = GetStreamM3U8Path(app, stream_key, False)
                if m3u8Path is None:
                    que.put(f'm3u8 not found')
                else:
                    que.put(m3u8Path)
                event.set()
                return

            # 搞一下文件夹
            rtmp_url = f"rtmp://{rtmp_host}/{app}/{stream_key}"
            currentTimeStr = datetime.now().strftime("%Y%m%d%H%M%S")
            stream_base_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}"
            hls_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}\\{currentTimeStr}"
            analyse_hls_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}\\{currentTimeStr}_analyse"
            hls_path = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}\\{currentTimeStr}\\stream_{stream_key}.m3u8"
            if not os.path.exists(stream_base_folder):
                os.makedirs(stream_base_folder)
            if not os.path.exists(hls_folder):
                os.makedirs(hls_folder)
            if not os.path.exists(analyse_hls_folder):
                os.makedirs(analyse_hls_folder)

            # 开个子进程抓流，转为hls
            capture_ori_cmd = [
                settings.FFMPEG_PATH,
                '-i', rtmp_url,
                '-rw_timeout', '5000000',
                '-c:v', 'h264_amf',
                '-c:a', 'aac',
                '-b:v', '500k',  # 设置视频比特率
                '-f', 'hls',
                '-hls_time', '1',
                '-hls_list_size', '10',
                hls_path
            ]


            print(' '.join(capture_ori_cmd))
            process = subprocess.Popen(capture_ori_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
            # 返回
            if process.poll() is not None :
                print(f"ffmpeg error: {process.poll()}")
                que.put(f'capture stream failure')
                event.set()
                return
            if not os.path.exists(hls_path):
                que.put(f'capture not start')
            else:
                que.put(f'hls/{stream_name}/{currentTimeStr}/stream_{stream_key}.m3u8')
            event.set()
            # 当前线程扫ts文件，进行检测
            currentID, failTime = 0, 0
            while True:
                oriPath = os.path.join(hls_folder, f"stream_{stream_key}{currentID}.ts")
                if not os.path.exists(oriPath):
                    failTime += 1
                    print(f'not found new ts file {failTime}')
                    if redisService.GetStreamDone(stream_name) is not None:
                        redisService.DoneStreamDone(stream_name)
                        print(f"stream done, break")
                        break
                    if failTime > 30:
                        print(f"cannot get new file for a long time: {hls_path}, maybe ffmpeg process failed, kill subprocess")
                        break
                    time.sleep(10)
                    continue
                ctx = AnalyseVideoForStreamTs(ctx, oriPath, stream_key, stream_name,
                                        currentID, currentTimeStr,
                                        analyse_hls_folder)
                failTime = 0
                currentID += 1
            ctx['ori_path'] = hls_folder
            ctx['analyse_path'] = analyse_hls_folder
            ctx['file_time'] = currentTimeStr
    except Exception as e:
        print("capture_ori_stream error", e)
    finally:
        redisService.DoneStreamDone(stream_name)
        if process is not None and process.poll() is None:
            process.kill()
        outputProcess = ctx.get('outputProcess')
        if outputProcess is not None and outputProcess.poll() is None:
            outputProcess.stdin.close()
            outputProcess.wait()
            outputProcess.terminate()
        print('capture return')
        if not event.is_set():
            event.set()

    if ctx.get('ori_path'):
        oriPath,analysePath, timeID, userID = ctx.get('ori_path'), ctx.get('analyse_path'), ctx.get('file_time'), -1
        oriUID = f"stream_replay_{stream_key}_{timeID}"
        analysedUID = f"analysed_{oriUID}"
        user = StreamKeyInfo.objects.filter(stream_key=stream_key).first()
        if user:
            userID = user.user_id
        oriFileInfo = resolve_ori_stream_to_fileinfo(oriPath, oriUID, userID)
        resolve_analysed_stream_to_fileinfo(analysePath, analysedUID, oriFileInfo)
    log.info('capture_streamNanalyse return')


def resolve_ori_stream_to_fileinfo(streamPath, fileUID, userID):
    destVideoPath = os.path.join(settings.MEDIA_ROOT, 'files', f'{fileUID}.mp4')
    # 合成mp4
    merge_video_files(streamPath, destVideoPath,'ts')
    # 缩略图
    FileManager().CreateThumbnail(destVideoPath, fileUID, FileType.Video.value)
    # 写db
    fileInfo = FileInfo.objects.createStreamFile(
        filename=f"{fileUID}.mp4",
        fileUID=fileUID,
        userID=userID,
        fileSize=FileManager().GetFileSize(destVideoPath),
    )
    FileManager().cutFile4Video(fileInfo)
    fileInfo.file_status = FileStatus.Done.value
    fileInfo.save()
    return fileInfo

def resolve_analysed_stream_to_fileinfo(streamPath, fileUID, oriFileInfo):
    destVideoPath = os.path.join(settings.MEDIA_ROOT, 'files', f'{fileUID}.mp4')
    # 合成mp4
    merge_video_files(streamPath, destVideoPath, 'ts')
    # 缩略图
    FileManager().CreateThumbnail(destVideoPath, fileUID, FileType.Video.value)
    # 写db
    fileInfo = FileInfo.objects.createAnalysedFile(oriFileInfo.id, fileUID, FileManager().GetFileSize(destVideoPath))
    FileManager().cutFile4Video(fileInfo)
    fileInfo.file_status = FileStatus.Done.value
    fileInfo.save()
    return fileInfo

def GetStreamM3U8Path(app, stream_key, isAnalyse=False):
    stream_name = f"{app}_{stream_key}"
    hls_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}"
    folders = os.listdir(hls_folder)
    if isAnalyse:
        folders = [f for f in folders if f.endswith('_analyse')]
    else:
        folders = [f for f in folders if not f.endswith('_analyse')]
    folders.sort()
    hls_path = f"hls/{stream_name}/{folders[-1]}/{'analysed_' if isAnalyse else ''}stream_{stream_key}.m3u8"
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, hls_path)):
        return hls_path
    else:
        return None

def AnalyseVideoForStreamTs(ctx, srcPath, stream_key, stream_name, currentID, streamTimeStr, destFolder):
    videoPath = GetFromModel(srcPath, f"stream_{stream_key}{currentID}", f"{stream_name}_{streamTimeStr}")
    outputProcess = ctx.get('outputProcess')
    if outputProcess is None:
        outputProcess = InitStreamOutput(videoPath, destFolder, f'analysed_stream_{stream_key}.m3u8', hlsListSize=6)
        ctx['outputProcess'] = outputProcess
    WriteFrameAsStream(outputProcess, videoPath)
    # while True:
    #     ret, frame = cap.read()
    #     if not ret:
    #         break
    #     # 将每一帧写入FFmpeg的标准输入
    #     outputProcess.stdin.write(frame.tobytes())
    return ctx

