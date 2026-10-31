# Deluxe Auto

Закрытый сайт записи в ателье для элитных авто. Тёплые клиенты оставляют заявку на визит; данные остаются на сервере.

Контур: **Nginx → статика + API**, FastAPI, Postgres, pgAdmin, локальный Docker Registry, Watchtower.

## Адреса

Подставьте IP сервера вместо `SERVER_IP` (в `.env`).

| Что | URL |
|---|---|
| Сайт / форма | `http://SERVER_IP/` |
| API | `http://SERVER_IP/api/` |
| Swagger (пока `ENABLE_DOCS=true`) | `http://SERVER_IP/docs` |
| pgAdmin | `http://SERVER_IP/pgadmin/` |
| Registry | `SERVER_IP:5000` (`docker login`) |

С хоста **не** открыты порты Postgres, backend и самого registry — только 80 и 5000 у Nginx.

## Состав

```
internet
  └─ Nginx :80  сайт (frontend/dist), /api, /docs, /pgadmin
     Nginx :5000  Docker Registry /v2/
        ├─ backend :8000     FastAPI (сети app + data)
        ├─ pgadmin :8080     только через /pgadmin/
        ├─ postgres :5432    только сеть data
        └─ registry :5000    только сеть registry_net
```

Сети Compose: `edge` (выход в интернет), `app`, `data`, `registry_net` (внутренние).

## Запуск

Нужны Docker Compose и файл `.env` (не в git).

```bash
cp .env.example .env
# Заполните пароли. Символ $ только в одинарных кавычках: POSTGRES_PASSWORD='YourPass$word'
chmod 600 .env
./scripts/init-secrets.sh   # если ещё нет htpasswd и .env
docker compose up -d
```

На VPS с ~700 МБ RAM не поднимайте всё сразу вместе с тяжёлым агентом. Сайт живёт на `nginx` + `backend` + `postgres` + `registry`. pgAdmin и Watchtower едят память — при обрывах сессии их лучше не держать:

```bash
docker compose up -d postgres backend nginx registry
docker compose up -d pgadmin    # по необходимости
```

После смены кода backend образ надо пересобрать **или** скопировать файлы в контейнер и `docker restart deluxe_backend`. Иначе контейнер останется на старой схеме колонок.

## Фронтенд

Сборка **не на маленьком VPS**, а локально. Nginx отдаёт только `frontend/dist`.

```bash
cd frontend
npm install
npm run build
```

После `npm run build` свежий `dist` сразу на сайте (bind-mount). Источники: `frontend/src`, `frontend/index.html`.

Форма шлёт пакет в `POST /api/leads` (заявка + behavior). Тип работ зависит от выбранной услуги.

Колонки заявки: `make`, `model`, `year`, `vehicle_details`, `service`, `work_type`, `work_area`, `visit_format`, `booked_by`, `needed_by`, контакты, `budget`.

## API

Префикс `/api`.

- `GET /api/health`
- `GET /api/admin` — услуги и ползунок бюджета
- `POST /api/leads` — заявка + опционально `behavior`
- CRUD `/api/leads`, `/api/behaviors`, `/api/admin`

Схема таблиц создаётся при старте backend из SQL в docstring моделей (`leads`, `behaviors`, `admin_settings`).

## Registry

```bash
docker login SERVER_IP:5000
# каталог: GET /v2/_catalog  (basic auth)
```

Корень `:5000/` отдаёт 404 — это нормально, нужен путь `/v2/`.

## Диск и память

VPS ~7 ГБ диска и ~700 МБ RAM. Журналы и логи Docker ограничены. Часовой `scripts/disk-guard.sh` чистит кэш и journal, **тома не трогает**. `docker system prune` только при занятости диска ≥ 90%.

Не ставьте Node и не собирайте Vite на этом VPS — место и RAM кончаются, SSH/Cursor отваливаются (OOM), помогает только перезагрузка.

Пароли с `$` в `.env` — в одинарных кавычках. Compose и Postgres снимают кавычки сами.

## Структура

```
backend/          FastAPI, модели, CRUD
frontend/         Vite, сборка в dist/
nginx/conf.d/     reverse proxy
pgadmin/          servers.json
scripts/          init-secrets.sh, disk-guard.sh
docker-compose.yml
```
