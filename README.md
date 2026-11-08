# GPU-CPU Switcher

**English:** A Linux utility for detecting GPUs and launching applications on a selected graphics processor.

**Русский:** Утилита для Linux, предназначенная для обнаружения видеокарт и запуска приложений на выбранном графическом процессоре.

---

## 🇬🇧 English

### Features
- Detects Intel, NVIDIA and AMD GPUs.
- Launches applications using a selected GPU.
- Checks the OpenGL renderer.
- Automatically detects installed applications.
- Supports custom applications.
- Dark and light themes.
- Optional MangoHud integration.

### Requirements
- Linux
- Python 3
- PyQt6
- pciutils
- mesa-utils

### Installation (Ubuntu)

sudo apt update
sudo apt install python3-pyqt6 pciutils mesa-utils

### Launch

python3 main.py

### Limitations
GPU launch verification currently supports Intel and NVIDIA. AMD detection is available, but launch verification is not implemented yet.

---

## 🇷🇺 Русский

### Возможности
- Обнаружение видеокарт Intel, NVIDIA и AMD.
- Запуск приложений на выбранной видеокарте.
- Проверка OpenGL.
- Автоматическое обнаружение установленных приложений.
- Добавление собственных приложений.
- Светлая и тёмная темы.
- Поддержка MangoHud.

### Требования
- Linux
- Python 3
- PyQt6
- pciutils
- mesa-utils

### Установка (Ubuntu)

sudo apt update
sudo apt install python3-pyqt6 pciutils mesa-utils

### Запуск

python3 main.py

### Ограничения
Проверка запуска пока поддерживает Intel и NVIDIA. Видеокарты AMD обнаруживаются, но проверка запуска для них ещё не реализована.

---

## License / Лицензия

MIT License.
