import time
from typing import AnyStr

GENERAL_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_local_epoch(format: AnyStr, epoch_time: int) -> AnyStr:
    """
    format epoch in local time based on provided format
    """
    return time.strftime(format, time.localtime(epoch_time))
