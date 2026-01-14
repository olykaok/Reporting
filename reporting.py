import json
import csv
import os
import sys
from math import ceil
import logging
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
from lib.jira_client import JiraClient
from lib.logger import setup_logger, check_existing_log, get_log_file_paths, write_log_entries

# Load environment variables
load_dotenv()
JIRA_URL = os.getenv('JIRA_URL')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')
MAX_RESULTS_PER_PAGE = int(os.getenv('MAX_RESULTS_PER_PAGE', 100))
JQL = os.getenv('JQL', '')
# ROUNDING_TYPE - тип округления времени: 'half_hour' (до получаса) или 'tenths' (до десятых)
ROUNDING_TYPE = os.getenv('ROUNDING_TYPE', 'half_hour')
INPUT_DIR = 'data/in'
OUTPUT_DIR = 'data/out'
CSV_DELIMITER = ','

# Initialize Jira client if credentials are available
jira_client = None
if JIRA_URL and JIRA_TOKEN:
    jira_client = JiraClient(JIRA_URL, JIRA_TOKEN, MAX_RESULTS_PER_PAGE)

def seconds_to_hours(seconds):
    """Конвертирует секунды в часы с округлением в зависимости от ROUNDING_TYPE"""
    if seconds is None:
        return 0
    
    # Конвертируем секунды в часы
    hours = seconds / 3600
    
    # Округляем в зависимости от типа округления
    if ROUNDING_TYPE == 'tenths':
        # Округляем до ближайшего 0.1 часа
        rounded_hours = round(hours * 10) / 10
    else:
        # По умолчанию округляем до ближайшего 0.5 часа
        rounded_hours = ceil(hours * 2) / 2
    
    return rounded_hours

def fetch_jira_data_to_json():
    """
    Получает данные из Jira по JQL и сохраняет их в JSON файл
    
    Returns:
        str: путь к созданному JSON файлу или None в случае ошибки
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
        json_filepath = os.path.join(INPUT_DIR, json_filename)
        
        # Создаем директорию если она не существует
        os.makedirs(INPUT_DIR, exist_ok=True)
        
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
    Обрабатывает JSON из Jira и создает два CSV файла
    
    Args:
        json_file_path (str): путь к JSON файлу
    """
    
    try:
        # Проверяем, что файл существует
        if not os.path.isfile(json_file_path):
            print(f"Ошибка: Файл {json_file_path} не найден")
            return
        
        # Генерируем имена выходных файлов на основе входного файла
        base_name = os.path.splitext(json_file_path)[0]
        output_file1 = f"{base_name}_tasks_detailed_final.csv"
        output_file2 = f"{base_name}_tasks_summary_final.csv"
        
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
    """Основная функция"""
    # Проверяем, передан ли файл в командной строке
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

# Пример использования
if __name__ == "__main__":
        main()
