# oboykin-spy
Oboykin Spy - ваш проводник к скидкам на обои ✨🧑‍🔧 

# Запуск

На машине должен быть установлен Docker и Docker Compose. Для запуска необходимо выполнить команду:

```
docker compose up --build -d
```

Чтобы остановить приложение:

```
docker compose down
```

# Создание таблиц в mart-postgres

Нужно выполнить скрипт для создания таблиц БД:

```
docker exec mart-postgres psql -U oboykin -d oboykin -f /init.sql
```