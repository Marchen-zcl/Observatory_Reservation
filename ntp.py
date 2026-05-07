import time

import requests
import win32api
from config_log import logger
from datetime import datetime, timezone


def get_network_time():
    response = requests.get("http://api.pinduoduo.com/api/server/_stm")
    data = response.json()
    server_time = data["server_time"]
    return datetime.fromtimestamp(server_time / 1000, tz=timezone.utc)


def set_system_time(network_time):
    system_time = (
        network_time.year,
        network_time.month,
        network_time.weekday(),
        network_time.day,
        network_time.hour,
        network_time.minute,
        network_time.second,
        network_time.microsecond // 1000,
    )
    win32api.SetSystemTime(*system_time)


def set_time():
    while True:
        try:
            logger.info(f"正在同步网络时间...")
            network_time = get_network_time()
            set_system_time(network_time)
            logger.info(f"同步成功！")
            break
        except Exception as e:
            logger.error(f"同步失败！正在尝试重新同步... error: {e}")
            time.sleep(1)
            continue


if __name__ == "__main__":
    set_time()
