import os

from utils.logger import logger


def load_test_files(directory) -> dict:
    """
    Загружает все файлы из указанной папки.
    :param directory: путь к папке с тестовыми файлами
    :return: словарь, где ключ – имя файла, значение – данные в байтах
    """
    test_files = {}
    if not os.path.exists(directory):
        logger.error(f"Папка {directory} не найдена.")
        raise FileNotFoundError(f"Папка {directory} не найдена.")

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        test_files[filename] = load_test_file(path)
    return test_files


def load_test_file(path) -> bytes:
    """
    Загружает файл по указанному пути.
    """
    if os.path.isfile(path):
        with open(path, "rb") as f:
            test_file = f.read()
    else:
        logger.error(f"Файл {path} не найден.")
        raise FileNotFoundError(f"Файл {path} не найден.")

    return test_file
