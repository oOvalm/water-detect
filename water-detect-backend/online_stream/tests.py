import cv2
import time

from online_stream.service import AnalyseFrame
from yolo.yolo_model.analyse import AnalyseImage




def TestCV2():
    stream_name = "home"
    try:
        # 输入流地址
        input_stream = f'rtmp://127.0.0.1:1935/live/{stream_name}'

        # 打开 RTMP 流
        cap = cv2.VideoCapture(input_stream, cv2.CAP_FFMPEG)
        # 检查是否成功打开流
        if not cap.isOpened():
            print(f"cannot open rtmp stream: {input_stream}")
            return

        # 获取视频的帧率
        fps = cap.get(cv2.CAP_PROP_FPS)
        # 计算 10 秒的帧数
        frames_per_10_seconds = int(fps * 60)

        frame_count = 0
        frame_list = []

        while True:
            ret, frame = cap.read()
            if not ret:
                print("cannot read frame skip")
                break
            # 调试信息：打印帧的最小值和最大值
            print(f"min frame: {frame.min()}, max frame: {frame.max()}")
            analysedFrame = AnalyseFrame(frame)
            # 将当前帧添加到帧列表中
            frame_list.append(analysedFrame)
            frame_count += 1

            # 当帧数达到 10 秒的帧数时
            if frame_count == frames_per_10_seconds:
                # 获取帧的宽度和高度
                height, width, _ = analysedFrame.shape
                # 定义视频编码器和输出文件名
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                output_filename = f'output_{int(time.time())}.mp4'
                # 创建视频写入对象
                out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

                # 将帧列表中的帧写入视频文件
                for f in frame_list:
                    out.write(f)

                # 释放视频写入对象
                out.release()
                print(f"Video saved: {output_filename}")

                # 清空帧列表和帧计数器
                frame_list = []
                frame_count = 0

        # 释放资源
        cap.release()
    except Exception as e:
        print(e)


def TestCV_one_img():

    stream_name = "home"
    try:
        # 输入流地址
        input_stream = f'rtmp://127.0.0.1:1935/live/{stream_name}'

        # 打开 RTMP 流
        cap = cv2.VideoCapture(input_stream, cv2.CAP_FFMPEG)
        # 检查是否成功打开流
        if not cap.isOpened():
            print(f"cannot open rtmp stream: {input_stream}")
            return

        # 获取视频的帧率
        fps = cap.get(cv2.CAP_PROP_FPS)
        # 计算 10 秒的帧数
        frames_per_10_seconds = int(fps * 10)

        frame_count = 0
        frame_list = []

        ret, frame = cap.read()
        if not ret:
            print("cannot read frame skip")
            return
        # 调试信息：打印帧的最小值和最大值
        print(f"min frame: {frame.min()}, max frame: {frame.max()}")
        analysedFrame = AnalyseFrame(frame)
        # 将当前帧添加到帧列表中
        frame_list.append(analysedFrame)
        frame_count += 1
        cv2.imwrite('before.jpg', frame)
        cv2.imwrite('after.jpg', analysedFrame)

        # 释放资源
        cap.release()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    # 调用函数
    TestCV2()

r"""
ffmpeg开启推流
ffmpeg.exe -re -i "D:\Videos\2024-02-01 19-21-23.mp4" -vcodec libx264 -acodec aac -f flv rtmp://127.0.0.1:1935/live/home
"""