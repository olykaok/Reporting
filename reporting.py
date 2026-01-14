"""
Модуль отчетности Jira

Этот модуль предоставляет функциональность для получения данных из Jira, их обработки
и генерации подробных отчетов в формате CSV. Поддерживает настраиваемые JQL-запросы,
опции округления времени и создает как детальные отчеты по задачам, так и сводную статистику.

Модуль может работать в трех режимах:
1. Получение данных из Jira с использованием JQL и их обработка
2. Обработка существующих JSON-файлов из входной директории
3. Обработка JSON-файла, переданного в качестве аргумента командной строки

Зависимости:
    - json: Для обработки JSON-данных
    - csv: Для генерации CSV-файлов
    - os: Для операций с файловой системой
    - sys: Для парсинга аргументов командной строки
    - math: Для математических операций (функция ceil)
    - datetime: Для генерации временных меток
    - dotenv: Для загрузки переменных окружения
    - lib.jira_client: Пользовательская реализация клиента Jira
"""

import json
import csv
import os
import sys
from math import ceil
# import logging
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
from lib.jira_client import JiraClient
# from lib.logger import setup_logger, check_existing_log, get_log_file_paths, write_log_entries

# Load environment variables
load_dotenv()
# Конфигурация Jira
JIRA_URL = os.getenv('JIRA_URL')
"""str или None: URL-адрес экземпляра Jira из переменных окружения"""

JIRA_TOKEN = os.getenv('JIRA_TOKEN')
"""str или None: Токен API Jira из переменных окружения"""

MAX_RESULTS_PER_PAGE = int(os.getenv('MAX_RESULTS_PER_PAGE', 100))
"""int: Максимальное количество результатов на страницу для запросов Jira API"""

JQL = os.getenv('JQL', '')
"""str: Строка JQL-запроса для фильтрации задач Jira"""

# ROUNDING_TYPE - тип округления времени: 'half_hour' (до получаса) или 'tenths' (до десятых)
ROUNDING_TYPE = os.getenv('ROUNDING_TYPE', 'tehnts')
"""str: Тип округления времени - 'half_hour' или 'tenths' (по умолчанию: 'tehnts')"""

INPUT_DIR = 'data/in'
"""str: Путь к директории входных JSON-файлов"""

OUTPUT_DIR = 'data/out'
"""str: Путь к директории выходных CSV-файлов"""

CSV_DELIMITER = ','
"""str: Символ-разделитель для CSV-файлов"""

# Инициализация клиента Jira при наличии учетных данных
jira_client = None
"""JiraClient или None: Инициализированный экземпляр клиента Jira при наличии учетных данных"""
if JIRA_URL and JIRA_TOKEN:
    jira_client = JiraClient(JIRA_URL, JIRA_TOKEN, MAX_RESULTS_PER_PAGE)


def seconds_to_hours(seconds, rounding = ROUNDING_TYPE):
    """
    Конвертирует секунды в часы с настраиваемым округлением.
    
    Аргументы:
        seconds (int или None): Время в секундах для конвертации
        rounding (str): Тип округления ('tenths' или 'half_hour')
    
    Возвращает:
        float: Время, конвертированное в часы с указанным округлением
               Возвращает 0, если seconds равно None
    
    Примеры:
        >>> seconds_to_hours(3600)  # 1 час
        1.0
        >>> seconds_to_hours(5400, 'half_hour')  # 1.5 часа
        1.5
        >>> seconds_to_hours(3660, 'tenths')  # 1.0167 часа -> 1.0
        1.0
    """
    if seconds is None:
        return 0
    
    # Конвертируем секунды в часы
    hours = seconds / 3600
    rounded_hours = round(hours * 100) / 100

    # Округляем в зависимости от типа округления
    if rounding == 'tenths':
        # Округляем до ближайшего 0.1 часа
        rounded_hours = round(hours * 10) / 10
    elif rounding == 'half_hour':
        # Округляем до ближайшего 0.5 часа
        rounded_hours = ceil(hours * 2) / 2
        
    return rounded_hours


def fetch_jira_data_to_json():
    """
    Получает данные из Jira с использованием JQL-запроса и сохраняет их в JSON-файл.
    
    Эта функция подключается к Jira с использованием настроенного клиента, выполняет JQL-запрос,
    получает все соответствующие задачи и сохраняет их в JSON-файл с временной меткой в
    выходной директории.
    
    Возвращает:
        str или None: Путь к созданному JSON-файлу, или None в случае ошибки
    
    Выбрасывает:
        Exception: Если возникли проблемы с подключением к Jira или получением данных
    
    Пример:
        >>> json_path = fetch_jira_data_to_json()
        >>> if json_path:
        ...     print(f"Данные сохранены в: {json_path}")
    """
    if not jira_client:
        print("Ошибка: Не удалось инициализировать Jira клиент")
        return None
    
    if not JQL or JQL.strip() == '':
        print("Ошибка: JQL не задан в файле .env")
        return None
    
    try:
        print(f"Получение данных из Jira по JQL: {JQL}")
        issues = jira_client.search_issues_by_jql(JQL)
        
        if not issues:
            print("Предупреждение: Не найдено задач по указанному JQL фильтру")
            return None
        
        # Создаем структуру данных в формате Jira API
        jira_data = {
            "issues": issues
        }
        
        # Создаем имя файла с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"jira_data_{timestamp}.json"
        json_filepath = os.path.join(OUTPUT_DIR, json_filename)
        
        # Создаем директорию если она не существует
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Сохраняем данные в JSON файл
        with open(json_filepath, 'w', encoding='utf-8') as file:
            json.dump(jira_data, file, ensure_ascii=False, indent=2)
        
        print(f"Данные успешно получены и сохранены в файл: {json_filepath}")
        print(f"Количество найденных задач: {len(issues)}")
        
        return json_filepath
        
    except Exception as e:
        print(f"Ошибка при получении данных из Jira: {str(e)}")
        return None


def process_jira_json(json_file_path):
    """
    Обрабатывает JSON-данные Jira и создает два CSV-файла отчетов.
    
    Эта функция читает задачи Jira из JSON-файла и генерирует два подробных отчета:
    1. Детальный отчет по задачам с информацией по каждой задаче
    2. Сводный отчет с агрегированной статистикой
    
    Функция извлекает различные поля из каждой задачи, включая:
    - Базовая информация о задаче (код, тип, название, статус)
    - Данные по учету времени (первоначальные оценки, затраченное время)
    - Пользовательские поля (направление, бизнес-процесс, версия, эпик)
    
    Аргументы:
        json_file_path (str): Путь к JSON-файлу, содержащему данные задач Jira
    
    Выбрасывает:
        FileNotFoundError: Если указанный JSON-файл не существует
        json.JSONDecodeError: Если JSON-файл содержит некорректные данные
        Exception: Для других ошибок обработки
    
    Пример:
        >>> process_jira_json('data/out/jira_data_20231201_120000.json')
        # Создает два CSV-файла в директории data/out/
    """
    
    try:
        # Проверяем, что файл существует
        if not os.path.isfile(json_file_path):
            print(f"Ошибка: Файл {json_file_path} не найден")
            return
        
        # Генерируем имена выходных файлов на основе входного файла
        # Извлекаем имя файла без пути и расширения
        json_filename = os.path.basename(json_file_path)
        base_name = os.path.splitext(json_filename)[0]
        # Формируем пути к выходным файлам в OUTPUT_DIR
        output_file1 = os.path.join(OUTPUT_DIR, f"{base_name}_tasks_detailed_final.csv")
        output_file2 = os.path.join(OUTPUT_DIR, f"{base_name}_tasks_summary_final.csv")
        
        # Создаем директорию если она не существует
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Чтение JSON файла
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Проверяем наличие необходимых данных
        if 'issues' not in data:
            print("Ошибка: В JSON отсутствует ключ 'issues'")
            return
        
        issues = data['issues']
        
        # Подготовка данных для первого файла
        detailed_data = []
        total_tasks = 0
        total_time_original_estimate_seconds = 0
        total_aggregate_time_original_estimate_seconds = 0
        total_time_spent_seconds = 0
        total_aggregate_time_spent_seconds = 0
        net_time_original_estimate_seconds = 0
        
        for issue in issues:
            # Извлекаем данные из полей
            key = issue.get('key', '')
            summary = issue.get('fields', {}).get('summary', '')
            
            # Извлекаем тип задачи
            issue_type = issue.get('fields', {}).get('issuetype', {}).get('name', '')
            
            # Извлекаем статус задачи
            status = issue.get('fields', {}).get('status', {}).get('name', '')
            
            # Извлекаем числовые поля (может быть None)
            time_original_estimate = issue.get('fields', {}).get('timeoriginalestimate')
            aggregate_time_original_estimate = issue.get('fields', {}).get('aggregatetimeoriginalestimate')
            time_spent = issue.get('fields', {}).get('timespent')
            aggregate_time_spent = issue.get('fields', {}).get('aggregatetimespent')
            
            # Извлекаем дополнительные поля
            fields = issue.get('fields', {})
            
            # Направление и Бизнес-процесс из customfield_12003
            direction = ''
            business_process = ''
            customfield_12003 = fields.get('customfield_12003')
            if customfield_12003:
                direction = customfield_12003.get('value', '')
                child = customfield_12003.get('child')
                if child:
                    business_process = child.get('value', '')
            
            # Версия из fixVersions
            version = ''
            fix_versions = fields.get('fixVersions', [])
            if fix_versions:
                version_names = [ver.get('name', '') for ver in fix_versions if ver.get('name')]
                version = ', '.join(version_names)
            
            # Задача Эпика из customfield_10102
            epic_task_key = fields.get('customfield_10102', '')
            
            # Эпик - название issue по ключу
            epic_name = ''
            if epic_task_key and jira_client:
                epic_name = jira_client.get_issue_summary(epic_task_key) or ''
            
            # Конвертируем в часы
            time_original_estimate_hours = seconds_to_hours(time_original_estimate)
            aggregate_time_original_estimate_hours = seconds_to_hours(aggregate_time_original_estimate)
            time_spent_hours = seconds_to_hours(time_spent)
            aggregate_time_spent_hours = seconds_to_hours(aggregate_time_spent)
            
            # Добавляем в детальные данные
            detailed_data.append([
                key,
                issue_type,
                summary,
                status,
                time_original_estimate_hours,
                aggregate_time_original_estimate_hours,
                time_spent_hours,
                aggregate_time_spent_hours,
                direction,
                business_process,
                version,
                epic_task_key,
                epic_name
            ])
            
            # Суммируем для сводной статистики
            total_tasks += 1
            total_time_original_estimate_seconds += time_original_estimate if time_original_estimate else 0
            total_aggregate_time_original_estimate_seconds += aggregate_time_original_estimate if aggregate_time_original_estimate else 0
            total_time_spent_seconds += time_spent if time_spent else 0
            total_aggregate_time_spent_seconds += aggregate_time_spent if aggregate_time_spent else 0
            
            # Считаем чистую первоначальную оценку (исключаем задачи с определенными статусами)
            if ((issue_type not in ["Ошибка тестового контура"]) and (status not in ["Ошибка тестового контура", "Отменено"])):
                net_time_original_estimate_seconds += time_original_estimate if time_original_estimate else 0
        
        # Запись первого файла (детальная информация)
        with open(output_file1, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='|')
            # Заголовки
            writer.writerow([
                'Код задачи',
                'Тип задачи',
                'Заголовок задачи', 
                'Статус задачи',
                'Первоначальная оценка (часы)',
                'Суммарная первоначальная оценка (часы)',
                'Затраченное время (часы)',
                'Суммарное затраченное время (часы)',
                'Направление',
                'Бизнес-процесс',
                'Версия',
                'Задача Эпика',
                'Эпик'
            ])
            # Данные
            writer.writerows(detailed_data)
        
        # Конвертируем суммарные значения в часы
        total_time_original_estimate_hours = seconds_to_hours(total_time_original_estimate_seconds)
        total_aggregate_time_original_estimate_hours = seconds_to_hours(total_aggregate_time_original_estimate_seconds)
        total_time_spent_hours = seconds_to_hours(total_time_spent_seconds)
        total_aggregate_time_spent_hours = seconds_to_hours(total_aggregate_time_spent_seconds)
        net_time_original_estimate_hours = seconds_to_hours(net_time_original_estimate_seconds)
        
        # Запись второго файла (сводная информация)
        with open(output_file2, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='|')
            # Заголовки
            writer.writerow([
                'Количество задач',
                'Общая первоначальная оценка (часы)',
                'Общая суммарная первоначальная оценка (часы)',
                'Общее затраченное время (часы)',
                'Общее суммарное затраченное время (часы)',
                'Чистая первоначальная оценка (часы)'
            ])
            # Данные
            writer.writerow([
                total_tasks,
                total_time_original_estimate_hours,
                total_aggregate_time_original_estimate_hours,
                total_time_spent_hours,
                total_aggregate_time_spent_hours,
                net_time_original_estimate_hours
            ])
        
        print(f"Обработка завершена успешно!")
        print(f"Обработано задач: {total_tasks}")
        print(f"Чистая первоначальная оценка рассчитана (исключены статусы: 'Ошибка тестового контура', 'Отменено')")
        print(f"Первый файл создан: {output_file1}")
        print(f"Второй файл создан: {output_file2}")
        
    except FileNotFoundError:
        print(f"Ошибка: Файл {json_file_path} не найден")
    except json.JSONDecodeError:
        print(f"Ошибка: Файл {json_file_path} содержит некорректный JSON")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


def main():
    """
    Основная точка входа для приложения отчетности Jira.
    
    Эта функция координирует весь процесс отчетности:
    1. Проверяет аргументы командной строки на наличие входного файла
    2. Ищет JSON-файлы во входной директории
    3. Получает новые данные из Jira, если файлы не найдены
    4. Обрабатывает данные и генерирует отчеты
    
    Функция реализует приоритетную обработку:
    - Аргумент командной строки (наивысший приоритет)
    - Файлы из входной директории (средний приоритет)  
    - Получение данных из Jira API (низший приоритет, резервный вариант)
    
    Использование:
        python reporting.py                          # Автоматический режим
        python reporting.py data/in/custom_file.json # Конкретный файл
    """
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
        print(f"Обрабатываем файл: {input_file}")
        process_jira_json(input_file)
        return
    
    # Проверяем наличие файлов в INPUT_DIR
    input_files = []
    if os.path.exists(INPUT_DIR):
        input_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    
    # Если есть JSON файлы в INPUT_DIR - обрабатываем их
    if input_files:
        print(f"Найдены файлы в директории {INPUT_DIR}: {input_files}")
        for input_file in input_files:
            file_path = os.path.join(INPUT_DIR, input_file)
            print(f"Обрабатываем файл: {file_path}")
            process_jira_json(file_path)
        return
    
    # Если нет файлов в INPUT_DIR - проверяем JQL и получаем данные из Jira
    print(f"В директории {INPUT_DIR} нет JSON файлов, проверяем JQL...")
    
    # Проверяем наличие JQL
    if not JQL or JQL.strip() == '':
        print("Ошибка: В директории нет файлов и не задан JQL фильтр в .env файле")
        print("Пожалуйста, добавьте JSON файл в директорию data/in или задайте JQL в .env")
        return
    
    # Получаем данные из Jira
    json_file_path = fetch_jira_data_to_json()
    if json_file_path:
        # Обрабатываем полученные данные
        process_jira_json(json_file_path)
    else:
        print("Не удалось получить данные из Jira")


if __name__ == "__main__":
        main()
