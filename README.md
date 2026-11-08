# GPU-CPU Switcher

Утилита для Linux, предназначенная для обнаружения видеокарт и запуска приложений на выбранном графическом процессоре.

## Features / Возможности

- Обнаружение видеокарт Intel, NVIDIA и AMD.
- Запуск приложений на выбранном GPU.
- Проверка OpenGL-рендерера.
- Автоматическое обнаружение установленных приложений.
- Добавление пользовательских приложений.
- Светлая и тёмная темы оформления.
- Дополнительная интеграция с MangoHud.

## Requirements / Требования

- Linux
- Python 3
- PyQt6
- pciutils
- mesa-utils

## Installation / Установка (Ubuntu)

Открой терминал и выполни команды по очереди:

```bash
sudo apt update
sudo apt install git python3 python3-pyqt6 pciutils mesa-utils
git clone https://github.com/nonamex143/GPU-CPU-Switcher.git
cd GPU-CPU-Switcher
```

## Launch / Запуск

```bash
python3 main.py
```

## Limitations / Ограничения

Приложение обнаруживает видеокарты Intel, NVIDIA и AMD. Проверка запуска приложений на выбранном GPU поддерживается для Intel и NVIDIA. Запуск приложений на AMD пока не реализован.

## License / Лицензия

MIT License.
