# Социальная сеть Yatube

**Yatube** - это сервис для публикации личных постов, где любой посетитель может просматривать посты и читать коммаентарии.
А после регистрации:
- Создать собственную страницу. Писать посты с картинками и добавлять их в сообщества.
- Подписываться на любимых авторов. 
- Комментировать записи.
- Управлять личным кабинетом (восстановить или сбросить пароль)


## Техническое описание

- Python 3.8
- Django 2.2

## Для локального запуска проекта выполните следующие дейтсивя

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/AlexeyPeresypkin/yatube.git
```
```
cd yatube
```
Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/bin/activate 
```

Обновить pip и установить зависимости:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Зайти в директорию приложения и выполнить миграции:
```
cd yatube/
```
```
python manage.py migrate
```
Перед загрузкой данных очистим БД
```
>>> python3 manage.py shell  
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()
```
Выполните загрузку данных в БД
```
python manage.py loaddata dump.json
```
При необходимости создать суперпользователя (login/email/password):
```
python manage.py createsuperuser
```
Запустить проект:

```
python manage.py runserver
```
### Проект будет доступеен по адресу http://127.0.0.1:8000/
### Панель администратора http://127.0.0.1:8000/admin/

