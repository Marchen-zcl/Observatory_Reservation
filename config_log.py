import logging
import time
import sys

# 定义颜色
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


# 定义一个函数来根据日志等级返回相应的颜色代码
def colorize_levelname(levelname):
    colors = {
        "DEBUG": "\033[0;34m",  # 蓝色
        "INFO": "\033[0;32m",  # 绿色
        "WARNING": "\033[0;33m",  # 黄色
        "ERROR": "\033[0;31m",  # 红色
        "CRITICAL": "\033[0;35m",  # 紫色
    }
    return colors.get(levelname, "\033[0m")  # 默认为无色


# 创建一个自定义的日志格式化器
class ColorizedFormatter(logging.Formatter):
    def format(self, record):
        original = super().format(record)
        levelname = colorize_levelname(record.levelname)
        colored_levelname = f"{levelname}[{record.levelname}]\033[0m"  # 重置颜色
        return original.replace(record.levelname, colored_levelname, 1)


# 定义一个函数来动态更新日志文件名
def get_log_file_handler():
    global current_date
    new_date = time.strftime("%Y-%m-%d", time.localtime())
    if new_date != current_date:
        current_date = new_date
    return logging.FileHandler(f"{current_date}.log", encoding="utf-8")


# 定义一个函数来动态更新日志文件handler
def update_file_handler():
    global current_date, file_handler
    new_date = time.strftime("%Y-%m-%d", time.localtime())
    if new_date != current_date:
        current_date = new_date
        new_file_handler = logging.FileHandler(f"{current_date}.log", encoding="utf-8")
        new_file_handler.setLevel(logging.DEBUG)
        new_file_handler.setFormatter(formatter2)
        logger.removeHandler(file_handler)  # 移除旧的handler
        logger.addHandler(new_file_handler)  # 添加新的handler
        file_handler = new_file_handler


# 修改日志记录时的逻辑，动态检查日期
class DynamicFileLogger(logging.Logger):
    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
    ):
        update_file_handler()  # 每次记录日志时检查并更新file_handler
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


# 替换默认的logger为动态更新的logger
logging.setLoggerClass(DynamicFileLogger)

# 创建一个logger
logger = logging.getLogger("self_global_logger")
logger.setLevel(logging.DEBUG)  # 设置logger的日志级别
# DEBUG < INFO < WARNING < ERROR < CRITICAL
# 当设置一个特定的日志等级时，所有该等级及更严重等级的日志消息都会被记录下来。例如，如果日志等级设置为WARNING，那么WARNING、ERROR和CRITICAL等级的日志消息都会被记录。

# 获取当前日期
current_date = time.strftime("%Y-%m-%d", time.localtime())

# 创建一个handler，用于写入日志文件, utf-8编码
file_handler = get_log_file_handler()
file_handler.setLevel(logging.DEBUG)  # 设置写入文件的日志级别

# 创建一个handler，用于输出到控制台
console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setLevel(logging.INFO)  # 设置输出到控制台的日志级别

# 定义handler的输出格式
formatter1 = ColorizedFormatter("%(asctime)s %(levelname)s - %(message)s")
formatter2 = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
file_handler.setFormatter(formatter2)
console_handler.setFormatter(formatter1)

# 给logger添加handler
logger.addHandler(file_handler)
logger.addHandler(console_handler)
