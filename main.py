#!/usr/bin/env python3
"""
Основная точка входа в проект.
Здесь происходит выбор тестовых данных, запуск экспериментов и вывод результатов.
"""

from experiments.experiment_entropy import experiment_entropy
from experiments.experiments import ExperimentRunner
from experiments.lzss_buffer_experiment import run_experiment
from utils.file_utils import load_test_files


def main():
    # Загрузка тестовых файлов
    test_files = load_test_files("data/input")

    # Инициализация прогона эксперимента для всех компрессоров
    runner = ExperimentRunner(test_files)
    runner.run_all()


if __name__ == "__main__":
    # Выбор эксперимента
    print("Выберите эксперимент для запуска:")
    print("1. Эксперимент сравнения энтропии для BWT+MTF")
    print("2. Эксперимент сравнения времени работы для всех компрессоров")
    print("3. Эксперимент зависимости коэффициента сжатия от размера буфера в LZSS")
    experiment = int(input("Введите номер эксперимента: "))

    if experiment == 1:
        experiment_entropy()
    elif experiment == 2:
        main()
    elif experiment == 3:
        run_experiment()
    else:
        print("Неверный номер эксперимента.")
