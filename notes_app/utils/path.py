from os import path


def get_file_updated_timestamp_as_epoch(file_path: str) -> int:
    """
    get file updated timestamp as epoch
    """
    return int(path.getmtime(file_path))


def get_file_size(file_path: str) -> int:
    """
    get file size
    """
    return path.getsize(file_path)
