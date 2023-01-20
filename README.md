# praktikum_new_diplom

### Проект "Продуктовый помошник"

Проект Продуктовый помошник позволяется создавать и удалять собственные рецепты, подписываться на авторов, сохранять рецепты в избранное и формировать список покупок. В проекте предусмотрена возвожность регистрации пользователей и смены пароля.
Проект создан с применением Python, Django, Django REST Framework и React.

## Как развернуть проект локально
1. Для запуска проекта требуется установить Docker
   (подробнее: https://cloud.yandex.ru/blog/posts/2022/03/docker-containers)
   Инструкцию по установке для Вашей операционной системы 
   можно найти по ссылке: https://docs.docker.com/desktop/install/mac-install/
2. Перейдите в папку infra и создайте файл .env с переменными окружения:
>DJANGO_DEBUG='' #DEBUG=False, для установки DEBUG=True введите любое другое значение 
>SECRET_KEY= #Укажите SECRET_KEY: https://www.educative.io/answers/how-to-generate-a-django-secretkey
>POSTGRES_DB=foodgram_db 
>POSTGRES_USER=postgres
>POSTGRES_PASSWORD=postgres
>DB_HOST=db
>DB_PORT=5432
3. Выполните следующие команды:
> docker-compose up
> docker-compose exec web python manage.py migrate
> docker-compose exec web python manage.py createsuperuser
Скопируйте CONTAINER ID контейнера web
> docker ps
Скопируйте файл базы данных в контейнер
> docker cp ../data/data.json CONTAINER ID:/app/data.json
Загрузите базу данных
> docker-compose exec web python manage.py loaddata data.json
> docker-compose exec web python manage.py collectstatic --no-input 
4. Проект будет доступен по адресу: http://localhost/
## Документация API
К проекту по адресу http://localhost/redoc/ подключена документация API Foodgram. В ней описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа.
