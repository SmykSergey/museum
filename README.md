# Сайт музея

Django + PostgreSQL + Docker + i18n (uk/en).

## Стек

- Python 3.14, Django 6.1
- PostgreSQL 16 (в Docker)
- django-modeltranslation (i18n моделей)
- django-ckeditor-5 (rich-text)
- python-dotenv (конфигурация)

## Структура

\`\`\`
museum/
├── backend/           # Django-проект
│   ├── config/        # настройки (base/dev/prod)
│   ├── apps/          # приложения: core, news, events, locations
│   ├── templates/
│   ├── static/
│   ├── locale/
│   └── media/
├── frontend/          # исходная вёрстка
└── docker-compose.yml # позже, для прода
\`\`\`

## Локальный запуск

\`\`\`bash
# 1. PostgreSQL в Docker
docker run -d --name museum-postgres \\
  -e POSTGRES_USER=museum \\
  -e POSTGRES_PASSWORD=museum_dev_pass \\
  -e POSTGRES_DB=museum \\
  -p 5432:5432 \\
  -v museum_pg_data:/var/lib/postgresql/data \\
  postgres:16

# 2. venv и зависимости
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # когда появится

# 3. Переменные окружения
cp .env.example .env
# отредактируй SECRET_KEY

# 4. Миграции и запуск
python manage.py migrate
python manage.py runserver
\`\`\`
