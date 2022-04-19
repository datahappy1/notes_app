import time


def format_epoch(format, epoch_time):
    return time.strftime(format, time.localtime(epoch_time))
