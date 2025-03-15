import logging
import subprocess
from threading import Thread

# 配置日志记录器
logger = logging.getLogger(__name__)

# 模拟 StringTools.isEmpty 方法
def is_empty(cmd):
    # 如果cmd是string
    if isinstance(cmd, list):
        return cmd is None or len(cmd) == 0
    return cmd is None or cmd.strip() == ""

class ProcessKiller(Thread):
    def __init__(self, process):
        Thread.__init__(self)
        self.process = process

    def run(self):
        try:
            self.process.terminate()
        except Exception as e:
            logger.error(f"终止进程时出错：{str(e)}")

class PrintStream(Thread):
    def __init__(self, stream):
        Thread.__init__(self)
        self.stream = stream
        self.string_buffer = ""

    def run(self):
        try:
            if self.stream is None:
                return
            for line in self.stream:
                self.string_buffer += line.decode('utf-8')
        except Exception as e:
            logger.error(f"读取输入流出错了！错误信息：{str(e)}")
        finally:
            try:
                if self.stream:
                    self.stream.close()
            except Exception as e:
                logger.error("调用 PrintStream 读取输出流后，关闭流时出错！")

def execute_command(cmd, outprint_log=False):
    if is_empty(cmd):
        logger.error("--- 指令执行失败，因为要执行的 FFmpeg 指令为空! ---")
        return None

    process = None
    try:

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        error_stream = PrintStream(process.stderr)
        input_stream = PrintStream(process.stdout)

        error_stream.start()
        input_stream.start()

        error_stream.join()
        input_stream.join()

        result = error_stream.string_buffer + input_stream.string_buffer

        if outprint_log:
            logger.info(f"执行命令:{cmd}，已执行完毕,执行结果:{result}")
        else:
            logger.info(f"执行命令:{cmd}，已执行完毕")

        return result
    finally:
        if process:
            killer = ProcessKiller(process)
            killer.start()

# 示例调用
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        result = execute_command("ls -l", True)
        print(result)
    except Exception as e:
        print(f"执行命令出错：{str(e)}")