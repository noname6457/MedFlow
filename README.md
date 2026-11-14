
# MedFlow

MedFlow — учебное веб-приложение для онлайн-записи
пациентов к врачам.

Проект разработан для изучения backend-разработки
на Python, Django и PostgreSQL.

## Возможности

- Регистрация и авторизация пациентов
- Каталог врачей с поиском и фильтрацией
- Просмотр информации о специалистах
- Получение свободного расписания
- Онлайн-бронирование приёмов
- Защита от двойного бронирования
- Просмотр и отмена собственных записей
- Автоматическая генерация расписания
- Управление данными через Django Admin

## Технологии

**Backend**
- Python
- Django
- Django REST Framework

**Database**
- PostgreSQL
- Django ORM

**Frontend**
- HTML5
- CSS3
- JavaScript
- Django Templates

**Testing**
- Django TestCase
- DRF APIClient
- unittest

## Архитектура

Приложение состоит из нескольких основных компонентов:

- `config` — настройки и маршрутизация Django
- `core` — модели врачей, расписания и бронирования
- `users` — регистрация и авторизация
- `templates` — HTML-шаблоны
- `static` — CSS и JavaScript

### Основные модели

- `Specialization` — медицинская специализация
- `Doctor` — врач
- `AppointmentSlot` — временной слот приёма
- `Appointment` — запись пациента на приём
- `User` — стандартная модель пользователя Django

### Бронирование

Для предотвращения двойной записи используются:

1. Транзакции `transaction.atomic()`
2. Блокировка строк `select_for_update()`
3. Уникальная связь `OneToOneField`

## API

| Метод | Endpoint | Назначение |
|-------|----------|------------|
| GET | /api/doctors/ | Каталог врачей |
| GET | /api/doctors/{id}/ | Информация о враче |
| GET | /api/doctors/{id}/slots/ | Свободные слоты |
| POST | /api/doctors/{id}/slots/{slot_id}/book/ | Запись |
| GET | /api/appointments/ | Мои записи |
| DELETE | /api/appointments/{id}/ | Отмена записи |
| POST | /api/auth/register/ | Регистрация |
| POST | /api/auth/login/ | Авторизация |
| POST | /api/auth/logout/ | Выход |
| GET | /api/auth/me/ | Текущий пользователь |

Для авторизации используются сессии Django.
Изменяющие запросы защищены CSRF.

## Установка

### 1. Клонирование

git clone <REPOSITORY_URL>

cd MedFlow

### 2. Виртуальное окружение

python -m venv .venv

Активация в Windows PowerShell:

.venv\Scripts\Activate.ps1

### 3. Зависимости

pip install -r requirements.txt

### 4. Конфигурация

Создайте файл `.env` на основе `.env.example`.

Настройте подключение к PostgreSQL.

### 5. Миграции

python manage.py migrate

### 6. Запуск

python manage.py runserver

Приложение будет доступно по адресу:

http://127.0.0.1:8000/

## Генерация расписания

python manage.py generate_schedule --doctor 1 --days 30

По умолчанию расписание создаётся на рабочие дни
с 09:00 до 18:00, с перерывом с 13:00 до 14:00.

## Тестирование

python manage.py test core users

Тесты проверяют авторизацию, бронирование,
права доступа, генерацию расписания и
некоторые аспекты работы ORM.

## Статус проекта

Учебный MVP.

Приложение использует демонстрационные данные
и не предназначено для обработки реальных
медицинских сведений.

## Автор

Разработано в качестве pet-проекта для
изучения Python Backend Development.
