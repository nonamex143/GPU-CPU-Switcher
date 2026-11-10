# GPU-CPU Switcher

Утилита для Linux, предназначенная для обнаружения видеокарт и запуска приложений на выбранном графическом процессоре.

**Разработка:** проект создан при помощи ChatGPT.  
**Среда разработки:** Ubuntu 24.04.

**Важно:** приложение разработано и проверено в Ubuntu 24.04. Я не гарантирую его работоспособность на других версиях Linux и других системах.

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
- X11 (Xorg) — Wayland пока не поддерживается.
## License / Лицензия

MIT License.

---

## English

A Linux utility for detecting GPUs and launching applications on a selected graphics processor.

**Development:** Created with the assistance of ChatGPT.  
**Development environment:** Ubuntu 24.04.

**Disclaimer:** The application was developed and tested on Ubuntu 24.04. I do not guarantee that it will work on other Linux distributions, versions, or systems.

## License

MIT License.
## Скриншот приложения
<img width="648" height="826" alt="image" src="https://github.com/user-attachments/assets/6f39b210-8406-4fe0-a77b-a0b290c1cef1" />


