import math

from moviepy.editor import VideoFileClip


def get_video_duration(file_path):
    try:
        clip = VideoFileClip(file_path)
        duration = clip.duration
        clip.close()
        return round(duration, 6)
    except Exception as e:
        print(f"get_video_duration error: {e}")
        return None

if __name__ == '__main__':
    duration = get_video_duration(r'D:\coding\graduation-design\water-detect\media\hls\live_remote\20250319164146\stream_remote98.ts')
    print("%.9f" % duration)