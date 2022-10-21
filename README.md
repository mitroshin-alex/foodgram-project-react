# Foodgram
![workflow status](https://github.com/mitroshin-alex/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg) \
сервер доступен по [ссылке](http://51.250.104.153/) admin/admin
### Описание
Блог, где вы можете найти рецепт для ужина на 100 персон 
или завтрака за 5 минут. \
У нас вы сможете поделиться своим фирменным рецептом или загрузить 
список продуктов для приготовления своих кулинарных экспериментов. \
Следите за понравившимися авторами и добавляйте рецепты в избранное.
### Технологии
- Python 3.7
- Django 2.2.16
- Djangorestframework 3.12.4
- Djoser 2.1.0
- Docker
- Docker compose
- Google
### Автоматическое тестирование и развертывание проекта на сервер
 - Заполнить секреты в GitHub
```Settings -> Secrets```\
Пример заполнения:
```
DEPLOY_HOST = 1.1.1.1
DEPLOY_KEY = -----BEGIN OPENSSH PRIVATE KEY-----
             dbvivvsfv98934ur09fnveuvBYU*(UGC^&U
             -----END OPENSSH PRIVATE KEY-----
DEPLOY_KEY_PASS = 123qwe
DEPLOY_USER = user
DOCKER_USERNAME = user
DOCKER_PASSWORD = 1234qwer
TELEGRAM_TO = 12345
TELEGRAM_TOKEN = 1111111111:dfvbjev7VVGVJHB8384-95JH
```
Плюс настройки для .env представленные ниже, \
не забудьте внести адрес сервера в список разрешенных
 - На сервере: \
Остановите службу nginx и отключить ее \
```sudo systemctl stop nginx``` \
```sudo systemctl disable nginx``` \
Установите docker \
```sudo apt install docker.io``` \
Установите docker compose \
[официальная документация](https://docs.docker.com/compose/install/) \
Скопировать \
```docker-compose.yaml``` в домашнюю директорию на сервер \
```nginx.conf``` в домашнюю директорию на сервер \
```frontend``` папку frontend в домашнюю директорию на сервер \
```docs``` папку docs в домашнюю директорию на сервер \
```data``` папку data в домашнюю директорию на сервер
 - Push commit проекта на GitHab
### Ручное развертывание проекта на сервере
### Пример заполнения .env
Файл .env должен располагаться в директории infra
```
SECRET_KEY=xxxxxxxxxxxxxxxx
ALLOWED_HOSTS=localhost;web
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123aaaBBBccc!
DB_HOST=db
DB_PORT=5432
``` 
- SECRET_KEY - секретный ключ проекта
- ALLOWED_HOSTS - список разрешенных хостов разделенных
- DB_ENGINE - движок базы данных
- DB_NAME - имя базы данных
- POSTGRES_USER - пользователь базы данных
- POSTGRES_PASSWORD - пароль POSTGRES_USER
- DB_HOST - имя сервера базы данных
- DB_PORT - порт DB_HOST
### Запуск проекта
- Перейти в директорию infra:
```
cd infra
``` 
- Запустить docker-compose:
```
docker compose up -d
``` 
- Применить миграции к базе данных:
```
docker compose exec web python manage.py migrate
```
- Создание суперпользователя:
```
docker compose web python manage.py createsuperuser
```
- Сбор статики:
```
docker compose exec web python manage.py collectstatic --no-input 
```
### Загрузка тестовых данных в BD (пользователи, теги, ингредиенты)
- В файле конфигурации проекта задать путь к папке с данными
```
По умолчанию
DATA_DIR = os.path.join(BASE_DIR, 'service/data/')
```
- В папке с файлом manage.py выполните команду:
```
sudo docker compose exec web python manage.py loadcsv
```
### Автор
Митрошин Алексей