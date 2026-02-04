Для забора данных из Jira будем использовать два метода API:
1) POST-запрос {{protocol}}://{{host}}/{{basePath}}tempo-timesheets/4/worklogs/export/filter

Body -- здесь могут быть заданы очень обширные параметры запроса:
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

Ответ от Jira 200 OK:
{
    "filterKey": "5db8906c9a9a496c8aa40e7453b2ea4a"
}
Это создался временный фильтр, и у него ID

2) Далее вторым шагом выполняется GET-запрос:
{{protocol}}://{{host}}/{{basePath}}tempo-timesheets/4/worklogs/export/{{filterId}}?format=csv
Значения для format - {csv, xlsx, pdf}
Значения по умолчанию - csv

