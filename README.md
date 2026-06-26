# QR Manager

Система управления динамическими QR-кодами. Создавайте, редактируйте и отслеживайте QR-коды с поддержкой категорий, пользователей и ролевой модели.

## Возможности

- Генерация динамических QR-кодов
- Категории для организации QR-кодов
- Ролевая модель: администратор, модератор, пользователь
- Привязка QR-кодов к конкретным пользователям
- Кастомные цвета и логотипы на QR-кодах
- Перенаправление через `/r/<key>`
- REST-подобные AJAX-эндпоинты в админ-панели
- Docker-развёртывание

## Быстрый старт

### Локально

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
cp .env.example .env       # настроить при необходимости
flask init-db              # создаёт БД + тестовые пользователи
python app.py              # http://localhost:5000
```

### Docker

```bash
docker build -t qr-manager .
docker run -d -p 5000:5000 --name qr-manager qr-manager
```

## Тестовые пользователи

| Логин | Пароль | Роль |
|---|---|---|
| `admin` | `admin123` | Администратор |
| `moderator` | `moder123` | Модератор |
| `user` | `user123` | Пользователь |

## Переменные окружения (`.env`)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-change-in-production` | Ключ подписи сессий Flask |
| `CSRF_SECRET_KEY` | `csrf-secret-key-change-in-production` | Ключ подписи CSRF-токенов |
| `DATABASE_URL` | `sqlite:///qrcodes.db` | URI базы данных |

Для production рекомендуется использовать PostgreSQL:

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## API Endpoints

Документация доступна на странице [/api](http://localhost:5000/api).

### Публичные

| Метод | Путь | Описание |
|---|---|---|
| GET | `/` | Главная |
| GET | `/login` | Вход |
| GET | `/r/<key>` | Редирект по ключу QR-кода |

### Требуют авторизации

| Метод | Путь | Описание |
|---|---|---|
| GET | `/dashboard` | Панель пользователя |
| GET | `/logout` | Выход |

### Админ-панель (admin/moderator)

| Метод | Путь | Описание |
|---|---|---|
| GET/POST | `/admin/dashboard` | Панель администратора |
| GET/POST | `/admin/create_user` | Создание пользователя |
| GET/POST | `/admin/edit_user/<id>` | Редактирование пользователя |
| GET | `/admin/delete_user/<id>` | Удаление пользователя |
| GET/POST | `/admin/create_category` | Создание категории |
| GET/POST | `/admin/edit_category/<id>` | Редактирование категории |
| GET | `/admin/delete_category/<id>` | Удаление категории |
| GET/POST | `/admin/generate_qr` | Создание QR-кода |
| GET/POST | `/admin/edit_qr/<id>` | Редактирование QR-кода |
| GET | `/admin/download_qr/<id>` | Скачивание QR-кода |
| GET | `/admin/delete_qr/<id>` | Удаление QR-кода |
| GET/POST | `/admin/site_settings` | Настройки сайта (только admin) |

## Технологии

- Python 3.12+
- Flask 2.3
- SQLAlchemy (SQLite / PostgreSQL / MySQL)
- Segno (генерация QR-кодов)
- Pillow (логотипы на QR-кодах)
- Docker

## Лицензия

MIT
