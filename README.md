# Image Converter (GUI)

[English](#english) | [Русский](#русский)

## English

A fast and simple Python 3.13 image converter with a clean GUI.
Supports batch conversion, drag & drop, quality presets, and custom output folders.

### Features
- Convert to PNG, WEBP, JPEG, BMP, TIFF, GIF
- Batch processing for multiple files
- Drag & drop (via `tkinterdnd2`)
- Quality presets for WEBP/JPEG
- Output folder selection and naming mode
- Mini preview and image metadata
- Animated UI

### Requirements
- Python 3.13
- Dependencies from `requirements.txt`

### Install
```bash
python -m pip install -r requirements.txt
```

### Run
```bash
python main.py
```

### Notes
- WEBP is lossless by default (can be changed via preset).
- JPEG uses high quality and optimization.

### Build (EXE)
```bash
python -m pip install pyinstaller
pyinstaller --onefile --windowed --clean --name ImageConverter --add-data "strings.json;." main.py
```
Result: `dist/ImageConverter.exe`

### Build (APK)
APK build requires Linux (or WSL). One option is Buildozer:
```bash
python -m pip install buildozer
buildozer init
```
Then edit `buildozer.spec` (set `requirements = python3,tkinter,Pillow,tkinterdnd2`) and run:
```bash
buildozer -v android debug
```
APK will be in `bin/`.

### Structure
- `main.py` — application
- `requirements.txt` — dependencies

### Ideas for future
- Progress by conversion stages and detailed log
- Preset profiles and last-used settings
- Batch resizing and filters

## Русский

Быстрый и простой конвертер изображений на Python 3.13 с удобным GUI.
Поддерживает пакетную конвертацию, drag & drop, пресеты качества и выбор папки вывода.

### Возможности
- Конвертация в PNG, WEBP, JPEG, BMP, TIFF, GIF
- Пакетная обработка списка файлов
- Drag & drop (через `tkinterdnd2`)
- Пресеты качества для WEBP/JPEG
- Выбор папки вывода и режима именования
- Мини‑превью и метаданные файла
- Анимированный UI

### Требования
- Python 3.13
- Зависимости из `requirements.txt`

### Установка
```bash
python -m pip install -r requirements.txt
```

### Запуск
```bash
python main.py
```

### Примечания
- Для WEBP используется lossless по умолчанию (можно изменить пресетом).
- Для JPEG включено высокое качество и оптимизация.

### Сборка (EXE)
```bash
python -m pip install pyinstaller
pyinstaller --onefile --windowed --clean --name ImageConverter --add-data "strings.json;." main.py
```
Результат: `dist/ImageConverter.exe`

### Сборка (APK)
Сборка APK требует Linux (или WSL). Один из вариантов — Buildozer:
```bash
python -m pip install buildozer
buildozer init
```
Далее правим `buildozer.spec` (указать `requirements = python3,tkinter,Pillow,tkinterdnd2`) и запускаем:
```bash
buildozer -v android debug
```
APK появится в `bin/`.

### Структура
- `main.py` — приложение
- `requirements.txt` — зависимости

### Идеи для развития
- Прогресс по шагам конвертации и детальный лог
- Профили настроек и сохранение последних параметров
- Добавление resizing и пакетных фильтров
