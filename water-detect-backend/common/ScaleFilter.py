import os
import subprocess

from PIL import Image
import logging

from common.ProcessUtils import execute_command
from waterDetect import settings

# 配置日志记录
logger = logging.getLogger(__name__)

def create_cover4video(source_file_path, width, target_file_path):
    """
    为视频创建封面
    :param source_file_path: 源视频文件路径
    :param width: 封面宽度
    :param target_file_path: 目标封面文件路径
    """
    try:
        # 构建 ffmpeg 命令
        cmd = [
            settings.FFMPEG_PATH,
            '-i', source_file_path,
            '-y',
            '-vframes', '1',
            '-vf', f'scale={width}:{width}/a',
            target_file_path
        ]
        print(cmd)
        # 执行命令
        execute_command(cmd)
    except Exception as e:
        # 记录错误日志
        logger.error(f"生成视频封面失败{e}", exc_info=True)

def create_thumbnail_width_ffmpeg(file_path, thumbnail_width, target_file_path, del_source):
    """
    使用 ffmpeg 创建缩略图
    :param file_path: 源文件路径
    :param thumbnail_width: 缩略图宽度
    :param target_file_path: 目标缩略图文件路径
    :param del_source: 是否删除源文件
    :return: 是否成功创建缩略图
    """
    try:
        # 打开图像
        with Image.open(file_path) as img:
            source_width = img.width
            source_height = img.height
            # 如果源图像宽度小于等于缩略图宽度，不进行处理
            if source_width <= thumbnail_width:
                return False
            # 压缩图像
            compress_image(file_path, thumbnail_width, target_file_path, del_source)
            return True
    except Exception as e:
        # 打印异常信息
        print(e)
    return False

def compress_image(source_file_path, width, target_file_path, del_source):
    """
    压缩图像
    :param source_file_path: 源文件路径
    :param width: 压缩后的宽度
    :param target_file_path: 目标文件路径
    :param del_source: 是否删除源文件
    """
    try:
        # 构建 ffmpeg 命令
        cmd = f"ffmpeg -i {source_file_path} -vf scale={width}:-1 {target_file_path} -y"
        # 执行命令
        execute_command(cmd)
        if del_source:
            # 删除源文件
            os.remove(source_file_path)
    except Exception as e:
        # 记录错误日志
        logger.error("压缩图片失败")


def cut_files(srcFilePath: str, destFolderPath: str, filename: str):
    # 定义 ffmpeg 命令模板
    tsPath = destFolderPath + '/index.ts'
    m3u8Path = destFolderPath + '/index.m3u8'
    # CMD_TRANSFER_2TS = [
    #     settings.FFMPEG_PATH, "-y",
    #     "-i", srcFilePath,
    #     "-vcodec", "copy",
    #     "-acodec", "copy",
    #     "-bsf:v", "h264_mp4toannexb",
    #     tsPath,
    # ]
    CMD_TRANSFER_2TS = [
        "ffmpeg",
        "-y",
        "-i", srcFilePath,
        "-c:v", "libx264",
        "-c:a", "copy",
        "-bsf:v", "h264_mp4toannexb",
        tsPath
    ]
    CMD_CUT_TS = [
        settings.FFMPEG_PATH,
        "-i", tsPath,
        "-c", "copy", "-map", "0", "-f", "segment", "-segment_list", m3u8Path,
        "-segment_time", "1", f"{destFolderPath}/{filename}_%04d.ts"
    ]
    print(' '.join(CMD_TRANSFER_2TS))
    print(' '.join(CMD_CUT_TS))

    # 生成 .ts 文件
    try:
        subprocess.run(CMD_TRANSFER_2TS)
        # execute_command(CMD_TRANSFER_2TS)
    except Exception as e:
        print(f"执行生成 .ts 文件的命令时出错: {e}")
        return

    # 生成索引文件 .m3u8 和切片 .ts
    try:
        subprocess.run(CMD_CUT_TS)
        # execute_command(CMD_CUT_TS)
    except Exception as e:
        print(f"执行生成 .m3u8 和切片 .ts 文件的命令时出错: {e}")
        return
    if os.path.exists(tsPath):
        os.remove(tsPath)