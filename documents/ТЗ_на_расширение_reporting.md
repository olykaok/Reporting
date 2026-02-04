
# Цель: добавление в reporting.py дополнительного функционала, который будет подключаться отдельным набором параметров в .env для сбора данных по фактическим часам за определённый период.

## На выходе: почти та же таблицы с данными, но с добавлением одного или нескольких столбцов, с данными по отработанным часам за определённый период.

Т.е. периоды в переменных среды должны задаваться массивом данных.
К массиву дат прилагается свой фильтр

### Для забора данных из Jira будем использовать метод API:
POST-запрос {{protocol}}://{{host}}/{{basePath}}tempo-timesheets/4/worklogs/search

Body -- здесь могут быть заданы очень обширные параметры запроса:
```json
{
  "from": "2026-01-01",
  "to": "2026-01-31",
//   "worker": [
//     "johnDoe"
//   ],
//   "taskId": [
//     12345
//   ],
//   "taskKey": [
//     "PROJ-1234"
//   ],
  "projectId": [
    11205
  ],
//   "projectKey": [
//     "PROJ"
//   ],
//   "teamId": [
//     12345
//   ],
//   "roleId": [
//     12345
//   ],
//   "accountId": [
//     12345
//   ],
//   "accountKey": [
//     "ACC"
//   ],
//   "filterId": [
//     12345
//   ],
//   "customerId": [
//     12345
//   ],
//   "categoryId": [
//     12345
//   ],
//   "categoryTypeId": [
//     12345
//   ],
//   "epicKey": [
//     "PROJ-1234"
//   ],
//   "locationIds": [
//     0
//   ],
  "includeSubtasks": true
}
```

### Ответ от Jira 200 OK:
```json
[
    {
        "billableSeconds": 18000,
        "timeSpent": "5h",
        "timeSpentSeconds": 18000,
        "issue": {
            "estimatedRemainingSeconds": 36000,
            "originalEstimateSeconds": 57600,
            "internalIssue": false,
            "projectId": 11205,
            "projectKey": "BA",
            "issueType": "Задача",
            "iconUrl": "/secure/viewavatar?size=xsmall&avatarId=10318&avatarType=issuetype",
            "summary": "Статистика: время ожидания клиента на КТ",
            "reporterKey": "JIRAUSER47329",
            "issueStatus": "Done",
            "versions": [
                13119
            ],
            "components": [],
            "key": "BA-812",
            "id": 78952
        },
        "tempoWorklogId": 235659,
        "comment": "Работа над запросом BA-812",
        "location": {
            "name": "Default Location",
            "id": 1
        },
        "attributes": {},
        "worker": "JIRAUSER56099",
        "updater": "JIRAUSER46647",
        "started": "2026-01-01 00:00:00.000",
        "originTaskId": 78952,
        "dateCreated": "2026-01-12 12:16:12.000",
        "dateUpdated": "2026-01-12 12:16:12.000",
        "originId": 235659
    },
    {
        "billableSeconds": 18000,
        "timeSpent": "5h",
        "timeSpentSeconds": 18000,
        "issue": {
            "estimatedRemainingSeconds": 36000,
            "originalEstimateSeconds": 57600,
            "internalIssue": false,
            "projectId": 11205,
            "projectKey": "BA",
            "issueType": "Задача",
            "iconUrl": "/secure/viewavatar?size=xsmall&avatarId=10318&avatarType=issuetype",
            "summary": "Статистика: время ожидания клиента на КТ",
            "reporterKey": "JIRAUSER47329",
            "issueStatus": "Done",
            "versions": [
                13119
            ],
            "components": [],
            "key": "BA-812",
            "id": 78952
        },
        "tempoWorklogId": 235660,
        "comment": "Работа над запросом BA-812",
        "location": {
            "name": "Default Location",
            "id": 1
        },
        "attributes": {},
        "worker": "JIRAUSER56099",
        "updater": "JIRAUSER46647",
        "started": "2026-01-02 00:00:00.000",
        "originTaskId": 78952,
        "dateCreated": "2026-01-12 12:16:12.000",
        "dateUpdated": "2026-01-12 12:16:12.000",
        "originId": 235660
    },
    {
        "billableSeconds": 9000,
        "timeSpent": "2h 30m",
        "timeSpentSeconds": 9000,
        "issue": {
            "internalIssue": false,
            "parentIssue": {
                "issueType": "Задача",
                "iconUrl": "/secure/viewavatar?size=xsmall&avatarId=10318&avatarType=issuetype",
                "summary": "Создать бот по оценке нарядов в MAX",
                "originalEstimateSeconds": 86400,
                "estimatedRemainingSeconds": 54900
            },
            "epicIssue": {
                "issueType": "Epic",
                "iconUrl": "/images/icons/issuetypes/epic.svg",
                "summary": "Путь клиента. Мониторинг оценки качества работы сотрудников"
            },
            "projectId": 11205,
            "projectKey": "BA",
            "issueType": "Подзадача",
            "iconUrl": "/secure/viewavatar?size=xsmall&avatarId=10316&avatarType=issuetype",
            "summary": "Посмотреть API Max",
            "parentKey": "BA-1069",
            "reporterKey": "JIRAUSER61206",
            "issueStatus": "Done",
            "epicKey": "K7-9299",
            "versions": [],
            "components": [],
            "key": "BA-1083",
            "id": 101982
        },
        "tempoWorklogId": 240291,
        "comment": "Подготовка отчета",
        "location": {
            "name": "Default Location",
            "id": 1
        },
        "attributes": {},
        "worker": "JIRAUSER29864",
        "updater": "JIRAUSER29864",
        "started": "2026-01-30 03:00:00.000",
        "originTaskId": 101982,
        "dateCreated": "2026-01-30 10:45:02.000",
        "dateUpdated": "2026-01-30 17:29:26.000",
        "originId": 240291
    }    
...
]
```

### Здесь важны параметры:
- "Key": "BA-1069" - номер задачи
- "parentKey": "BA-1069" - если указан, то текущая задача - подзадача 
- "timeSpentSeconds" - время потраченное на задачу в секундах
- Записи по одной задаче могут повторяться в выгрузке данных могут повторяться.

## План работы:
1. Массив входных фильтров должен иметь возможность принимать данные в формате JSON, пример:
```json
[
{
  "from": "2026-01-01",
  "to": "2026-01-31",
  "projectId": [
    11205
  ],
  "includeSubtasks": true
},
{
  "from": "2026-02-01",
  "to": "2026-02-28",
   "filterId": [
     12345
   ],
  "includeSubtasks": true
}
]   
```

Возможно, не стоит использовать .env,а использовать альтернативный файл в формате json с определенным названием. В .env оставить только логическое свойство - например "ADD_HOURS_BY_PERIODS=1"

1. Нужно получить данные по каждому из массива данных в фильтре. 
2. Для каждого ответа по фильтру -- просуммировать часы основной задаче (если у задачи есть подзадача, суммировать часы в родительскую, подзадачу в финальный массив не выводить).
3. Собрать данные по фильтрам в единый массив, например, в формате:
```json
[
    {
        "key": "BA-1234",
        "hours": [
            {
                "from": "2026-01-01",
                "to": "2026-01-31",
                "timeSpent": "25,5", // суммарное время в часах с округление, указанным в ROUNDING_TYPE
            },
            {
                "from": "2026-02-01",
                "to": "2026-02-28",
                "timeSpent": "5", // суммарное время в часах с округление, указанным в ROUNDING_TYPE
            },            
        ]
    },
    {
        "key": "BA-4321",
        "hours": [
            {
                "from": "2026-01-01",
                "to": "2026-01-31",
                "timeSpent": "5", // суммарное время в часах с округление, указанным в ROUNDING_TYPE
            }
        ]   
    }
]
```
4. И дальше отдать список задач в текущий process_jira_json, за тем исключением, что там будут дополнительные данные, которые надо будте обработать для вывода в CSV

5. В выводе в CSV дополнителные столбцы должны иметь названия периодов из фильтра,например: "2026-01-01:2026-01-31" или подобное.








            

