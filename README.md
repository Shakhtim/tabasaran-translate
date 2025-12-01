# Табасаранско-русский переводчик

Веб-приложение для перевода между табасаранским и русским языками.

## Архитектура

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vue.js        │────▶│   FastAPI       │────▶│   GPU Server    │
│   Frontend      │     │   Backend       │     │   (LLM)         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │   SQLite +      │
                        │   ChromaDB      │
                        └─────────────────┘
```

## Требования

### Локальный сервер (8 ГБ RAM)
- Python 3.11+
- Node.js 18+
- Tesseract OCR (для извлечения словаря)
- Poppler (для pdf2image)

### GPU сервер (опционально)
- Ollama или vLLM
- Mistral-7B / Qwen2-7B

## Установка

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Frontend

```bash
cd frontend
npm install
```

### 3. Tesseract OCR (для извлечения словаря)

Windows:
1. Скачать установщик: https://github.com/UB-Mannheim/tesseract/wiki
2. Установить с русским языком
3. Добавить в PATH

### 4. Poppler (для pdf2image)

Windows:
1. Скачать: https://github.com/oschwartz10612/poppler-windows/releases
2. Распаковать и добавить `bin` в PATH

## Извлечение словаря

```bash
# Тест OCR на одной странице
python scripts/extract_dictionary.py --test 10

# Полное извлечение
python scripts/extract_dictionary.py --full

# Импорт в базу данных
python scripts/import_dictionary.py --json backend/data/dictionary_raw.json

# Или импорт тестовых данных
python scripts/import_dictionary.py --sample
```

## Запуск

### Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

Приложение будет доступно на http://localhost:3000

## API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/translate` | Перевод текста |
| GET | `/api/dictionary/lookup/{word}` | Поиск слова |
| GET | `/api/dictionary/suggest?q=...` | Автодополнение |
| GET | `/api/dictionary/word/{id}` | Детали слова |
| GET | `/health` | Проверка статуса |

## Настройка GPU сервера

### Ollama
```bash
# Установка модели
ollama pull mistral:7b

# Запуск сервера
ollama serve
```

### Конфигурация
В `backend/.env`:
```
LLM_SERVER_URL=http://your-gpu-server:11434
LLM_MODEL=mistral:7b
```

## Структура проекта

```
tabasaran-translate/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI приложение
│   │   ├── config.py         # Настройки
│   │   ├── database.py       # SQLite
│   │   ├── models.py         # Pydantic модели
│   │   ├── services/
│   │   │   ├── translator.py # Движок перевода
│   │   │   ├── dictionary.py # Словарный поиск
│   │   │   ├── morphology.py # Морфология
│   │   │   └── llm_client.py # LLM клиент
│   │   └── routers/
│   │       ├── translate.py
│   │       └── dictionary.py
│   └── data/
│       └── dictionary.db
├── frontend/
│   └── src/
│       ├── App.vue
│       ├── components/
│       ├── composables/
│       └── api/
├── content/                   # Исходные PDF
└── scripts/
    ├── extract_dictionary.py
    └── import_dictionary.py
```

## Лицензия

MIT
