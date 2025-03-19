import logging
import os

import ffmpeg
from moviepy.editor import VideoFileClip

from common.ProcessUtils import execute_command

logger = logging.getLogger(__name__)

def avi_to_ts(input_file, output_file):
    """
    将AVI文件转换为TS文件。

    :param input_file: 输入的AVI文件路径
    :param output_file: 输出的TS文件路径
    """
    print('start convert avi to ts', input_file, output_file)
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_file
    ]
    execute_command(cmd, True)

def ts_to_avi(input_file, output_file):
    try:
        # 加载 .ts 视频文件
        clip = VideoFileClip(input_file)
        # 将视频保存为 .avi 格式
        clip.write_videofile(output_file, codec='mpeg4')
        # 关闭视频剪辑对象
        clip.close()
        print(f"成功将 {input_file} 转换为 {output_file}")
    except Exception as e:
        print(f"转换过程中出现错误: {e}")

def merge_video_files(input_folder, output_file, src_file_type):
    """
    将指定文件夹中的所有TS视频文件合并为一个视频文件

    :param input_folder: 包含TS视频文件的文件夹路径
    :param output_file: 合并后视频文件的输出路径
    """
    from moviepy.editor import VideoFileClip, concatenate_videoclips
    logger.info(f"start merge {src_file_type} to mp4, src_folder: {input_folder}, destFileName: {output_file}")
    # 获取文件夹中所有的TS文件
    ts_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(f'.{src_file_type}')]
    # 按文件名排序
    ts_files.sort()

    # 加载所有视频剪辑
    clips = [VideoFileClip(ts_file) for ts_file in ts_files]

    # 合并所有视频剪辑
    final_clip = concatenate_videoclips(clips, method="compose")

    # 保存合并后的视频
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')

    # 关闭所有视频剪辑对象以释放资源
    for clip in clips:
        clip.close()
    final_clip.close()


