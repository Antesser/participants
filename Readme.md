Приложение для работы с пользователями.

перво-наперво следует создать файлик .env и указать следующие параметры для подключения к БД и отправки писем:

DB_HOST = postgres_db
DB_PORT = 5432
DB_NAME = postgres
DB_USER = postgres
DB_PASS = postgres
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=
MAIL_SERVER=
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True
VALIDATE_CERTS=True


для запуска необходимо ввести команду make compose, затем пройти по ссылке http://localhost:5000/docs на сваггер

воспользоваться эндпоинтом /api/clients/create (который не должен быть глаголом согласно REST) для создания пользователя, авторизация в правом верхнем углу по email в качестве логина (о которой в ТЗ не было ни слова).

авторизованному пользователю доступны эндпоинты /api/clients/{id}/match и /api/list для оценки и получения списка участников соответственно (очень странно, что первые два эндпоинта имеют префикс /api/clients, а последний - нет, пришлось раскидывать по разным модулям, но, имхо, не комильфо), фильтрация реализована.

в коде указал дополнительные комментарии.


