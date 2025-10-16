import logging
from logging.handlers import TimedRotatingFileHandler
import os
from operator import truediv


def get_logger(name="file_collate", when="midnight", interval=1, backup_count=3):

    # 确定日志文件地址
    log_dir = os.path.abspath(os.path.join("../runtime_log"))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "program_running.log")
    os.makedirs(log_file,exist_ok=True)

    # 创建logger实例并且设置最低等级为debug
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复创建handlers
    if logger.handlers:
        return logger

    # 文件 handler：按时间切分，每天一个文件，保留3个历史文件
    try:
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when=when,            # "midnight" 表示每天轮转
            interval=interval,
            backupCount=backup_count,
            encoding="utf-8",
            utc=False
        )
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"无法创建文件日志 handler: {e}")

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(" %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)  # 控制台只输出 INFO 及以上
    logger.addHandler(console_handler)

    return logger
