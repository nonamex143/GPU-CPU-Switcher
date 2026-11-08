from PyQt6.QtGui import QIcon, QGuiApplication
from PyQt6.QtCore import QSettings, QTimer, Qt
import sys
import os
import re
import shlex
import configparser
import json
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QDialog, QHBoxLayout, QCheckBox, QInputDialog
)


def detect_gpus():
    result = subprocess.run(
        ["lspci", "-D", "-nn"],
        capture_output=True, text=True
    )

    cards = []

    for line in result.stdout.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue

        address, description = parts

        if not any(x in description for x in (
            "VGA compatible controller",
            "3D controller",
            "Display controller"
        )):
            continue

        if "NVIDIA" in description.upper():
            vendor = "NVIDIA"
        elif "INTEL" in description.upper():
            vendor = "Intel"
        elif "AMD" in description.upper() or "ATI" in description.upper():
            vendor = "AMD"
        else:
            vendor = "OTHER"

        pci = "pci-" + re.sub(r"[:.]", "_", address)
        name = description.split(": ", 1)[-1]

        cards.append({
            "label": f"{name} ({address})",
            "vendor": vendor,
            "pci": pci
        })

    return cards


def get_renderer(env):
    try:
        result = subprocess.run(
            ["glxinfo", "-B"],
            capture_output=True,
            text=True,
            env=env,
            timeout=12
        )
    except FileNotFoundError:
        return None, "Не найден glxinfo. Нужен пакет mesa-utils."
    except subprocess.TimeoutExpired:
        return None, "Проверка видеокарты превысила время ожидания."

    match = re.search(
        r"OpenGL renderer string:\s*(.+)",
        result.stdout
    )

    if not match:
        return None, result.stderr.strip() or "Не удалось определить GPU."

    return match.group(1).strip(), None


def renderer_matches(vendor, renderer):
    name = renderer.lower()

    if vendor == "Intel":
        return "intel" in name

    if vendor == "NVIDIA":
        return (
            any(x in name for x in (
                "nvidia", "nouveau", "geforce", "gt218"
            ))
            or bool(re.search(r"\bnv[a-z0-9]{2,}\b", name))
        )

    return False



def show_notice(title, color, details=""):
    box = QMessageBox()
    box.setWindowTitle("GPU-CPU Switcher")
    box.setText(
        f'<span style="color:{color}; font-size:18pt; '
        f'font-weight:bold">{title}</span>'
    )
    if details:
        box.setInformativeText(details)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()



class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Настройки")
        self.setFixedSize(320, 180)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Тема оформления:"))
        self.theme = QComboBox()
        self.theme.addItem("Тёмная", "dark")
        self.theme.addItem("Светлая", "light")
        self.theme.setCurrentIndex(
            self.theme.findData(parent.settings.value("theme", "dark"))
        )
        self.theme.currentIndexChanged.connect(self.save)
        layout.addWidget(self.theme)

        self.fps = QCheckBox("Показывать счётчик FPS")
        self.fps.setChecked(parent.settings.value("show_fps", False, type=bool))
        self.fps.toggled.connect(self.save)
        layout.addWidget(self.fps)

    def save(self):
        self.parent_window.settings.setValue("theme", self.theme.currentData())
        self.parent_window.settings.setValue("show_fps", self.fps.isChecked())
        self.parent_window.apply_theme()



def scan_apps():
    apps = {}
    data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
    roots = [os.path.join(data_home, "applications")]
    roots += [os.path.join(d, "applications") for d in data_dirs]

    for root in roots:
        if not os.path.isdir(root):
            continue
        for folder, _, files in os.walk(root):
            for filename in files:
                if not filename.endswith(".desktop"):
                    continue
                path = os.path.join(folder, filename)
                try:
                    cfg = configparser.ConfigParser(interpolation=None, strict=False)
                    cfg.read(path, encoding="utf-8")
                    entry = cfg["Desktop Entry"]
                    if entry.get("Type") != "Application" or entry.getboolean("Hidden", fallback=False) or entry.getboolean("NoDisplay", fallback=False):
                        continue
                    categories = set(entry.get("Categories", "").split(";"))
                    if categories.intersection({"Settings", "System", "PackageManager", "Screensaver"}):
                        continue
                    name = entry.get("Name", "").strip()
                    command = re.sub(r"%[fFuUdDnNickvm]", "", entry.get("Exec", "")).replace("%%", "%").strip()
                    if name and command and name != "GPU-CPU Switcher":
                        apps.setdefault(name, command)
                except Exception:
                    pass
    return sorted(apps.items(), key=lambda item: item[0].lower())


class GPUSwitcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPU-CPU Switcher")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")))
        self.resize(440, 320)

        self.settings = QSettings("GPU-Switcher", "GPU-Switcher")
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("GPU SWITCHER"))
        top.addStretch()
        gear = QPushButton("⚙")
        gear.setFixedWidth(45)
        gear.clicked.connect(self.open_settings)
        top.addWidget(gear)
        layout.addLayout(top)
        self.apply_theme()

        self.gpus = QComboBox()
        detected = detect_gpus()
        for card in detected:
            self.gpus.addItem(card["label"], card)
        for i, card in enumerate(detected):
            if card["vendor"] == "NVIDIA" or (card["vendor"] == "AMD" and "RX" in card["label"].upper()) or (card["vendor"] == "Intel" and "ARC" in card["label"].upper()):
                self.gpus.setCurrentIndex(i)
                break

        layout.addWidget(QLabel("Выбери видеокарту:"))
        layout.addWidget(self.gpus)

        layout.addWidget(QLabel("Установленные приложения:"))
        self.app_selector = QComboBox()
        self.app_selector.addItem("— Выбрать приложение —")
        self.app_selector.currentIndexChanged.connect(self.select_app)
        layout.addWidget(self.app_selector)

        add_app = QPushButton("＋ Добавить приложение")
        add_app.clicked.connect(self.add_custom_app)
        layout.addWidget(add_app)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_apps)
        self.refresh_timer.start(300000)
        self.refresh_apps()

        layout.addWidget(QLabel("Или введи команду вручную:"))
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText(
            "Например: glxgears"
        )
        layout.addWidget(self.app_input)

        browse = QPushButton("Выбрать файл")
        browse.clicked.connect(self.browse_file)
        layout.addWidget(browse)

        launch = QPushButton("ПРОВЕРИТЬ И ЗАПУСТИТЬ")
        launch.clicked.connect(self.launch_app)
        layout.addWidget(launch)

        self.status = QLabel("Готово к запуску")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

    def refresh_apps(self):
        current = self.app_selector.currentData()
        self.app_selector.blockSignals(True)
        self.app_selector.clear()
        self.app_selector.addItem("— Выбрать приложение —", None)
        apps = dict(scan_apps())
        try:
            custom_apps = json.loads(self.settings.value("custom_apps", "[]"))
        except (TypeError, ValueError):
            custom_apps = []
        for app in custom_apps:
            if isinstance(app, dict) and app.get("name") and app.get("command"):
                apps[app["name"]] = app["command"]
        for name, command in sorted(apps.items(), key=lambda item: item[0].lower()):
            self.app_selector.addItem(name, command)
        index = self.app_selector.findData(current)
        if index >= 0:
            self.app_selector.setCurrentIndex(index)
        self.app_selector.blockSignals(False)

    def add_custom_app(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать исполняемый файл")
        if not path:
            return
        name, ok = QInputDialog.getText(
            self, "Добавить приложение", "Название приложения:",
            text=os.path.basename(path)
        )
        if not ok or not name.strip():
            return
        try:
            custom_apps = json.loads(self.settings.value("custom_apps", "[]"))
        except (TypeError, ValueError):
            custom_apps = []
        custom_apps = [a for a in custom_apps if a.get("name") != name.strip()]
        custom_apps.append({"name": name.strip(), "command": shlex.quote(path)})
        self.settings.setValue("custom_apps", json.dumps(custom_apps, ensure_ascii=False))
        self.refresh_apps()
        index = self.app_selector.findData(shlex.quote(path))
        if index >= 0:
            self.app_selector.setCurrentIndex(index)

    def select_app(self, index):
        command = self.app_selector.itemData(index)
        if command:
            self.app_input.setText(command)

    def apply_theme(self):
        dark = self.settings.value("theme", "dark") == "dark"
        if dark:
            colors = ("#171923", "#edf0fa", "#252a3a", "#5146bd")
        else:
            colors = ("#f3f5fa", "#202536", "#ffffff", "#5265c7")
        bg, fg, field, accent = colors
        QApplication.instance().setStyleSheet(f"""
            QWidget {{ background: {bg}; color: {fg}; font-size: 10pt; }}
            QComboBox, QLineEdit {{ background: {field}; border: 1px solid #888;
                border-radius: 9px; padding: 10px; }}
            QPushButton {{ background: {accent}; color: white; border: none;
                border-radius: 10px; padding: 11px; font-weight: bold; }}
            QPushButton:hover {{ opacity: 0.8; }}
            QCheckBox {{ spacing: 8px; }}
        """)

    def open_settings(self):
        SettingsDialog(self).exec()

    def show_gpu_toast(self, card):
        toast = QWidget()
        toast.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        toast.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        layout = QVBoxLayout(toast)
        label = QLabel(f"GPU ACTIVE\\n{card['label']}")
        label.setWordWrap(True)
        layout.addWidget(label)

        toast.setStyleSheet("""
            QWidget {
                background-color: #202b40;
                color: #8cf2b8;
                border: 1px solid #38bdf8;
                border-radius: 12px;
                padding: 10px;
                font-weight: bold;
            }
        """)

        toast.adjustSize()
        screen = QGuiApplication.primaryScreen()
        if screen:
            area = screen.availableGeometry()
            toast.move(area.right() - toast.width() - 20, area.top() + 20)

        self.gpu_toast = toast
        toast.show()
        QTimer.singleShot(5000, toast.close)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать приложение"
        )
        if path:
            self.app_input.setText(path)

    def launch_app(self):
        command = self.app_input.text().strip()
        card = self.gpus.currentData()

        if not command:
            self.status.setText("Укажи приложение!")
            return

        if not card:
            self.status.setText("Видеокарты не обнаружены.")
            return

        try:
            args = shlex.split(command)
            env = os.environ.copy()
            env.pop("DRI_PRIME", None)

            vendor = card["vendor"]
            renderer = None

            if vendor == "Intel":
                renderer, error = get_renderer(env)

                if not renderer_matches("Intel", renderer or ""):
                    raise RuntimeError(
                        f"Выбрана Intel, но проверка показала: "
                        f"{renderer or error}"
                    )

            elif vendor == "NVIDIA":
                attempts = ["1", card["pci"]]

                for method in attempts:
                    test_env = env.copy()
                    test_env["DRI_PRIME"] = method

                    renderer, error = get_renderer(test_env)

                    if renderer_matches("NVIDIA", renderer or ""):
                        env = test_env
                        break
                else:
                    raise RuntimeError(
                        f"NVIDIA не прошла проверку. "
                        f"Обнаружено: {renderer or error}. "
                        "Запуск отменён, чтобы не использовать Intel."
                    )

            else:
                raise RuntimeError(
                    "Проверка пока поддерживает Intel и NVIDIA."
                )

            self.status.setText(
                f"Проверка пройдена: {renderer}. Запускаю!"
            )
            if self.settings.value("show_fps", False, type=bool):
                import shutil
                if not shutil.which("mangohud"):
                    raise RuntimeError("MangoHud не установлен: sudo apt install mangohud")
                args = ["mangohud", "--dlsym"] + args

            subprocess.Popen(args, env=env)
            self.show_gpu_toast(card)

        except Exception as e:
            self.status.setText(f"Ошибка: {e}")
            show_notice("ОШИБКА!!!!", "#dc2626", str(e))


app = QApplication(sys.argv)

# FLUENT_THEME
app.setStyleSheet("""
QWidget {
    background-color: #171923;
    color: #edf0fa;
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
}
QWidget#mainWindow {
    background-color: #171923;
}
QLabel {
    color: #cbd2e8;
    padding: 3px;
}
QComboBox, QLineEdit {
    background-color: #252a3a;
    border: 1px solid #414963;
    border-radius: 9px;
    padding: 10px;
    selection-background-color: #6558d3;
}
QComboBox:hover, QLineEdit:hover {
    border: 1px solid #8175ed;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QPushButton {
    background-color: #5146bd;
    border: none;
    border-radius: 10px;
    padding: 11px 16px;
    color: white;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #675be0;
}
QPushButton:pressed {
    background-color: #40369c;
}
QMessageBox {
    background-color: #202536;
}
QMessageBox QLabel {
    color: #edf0fa;
}
""")

window = GPUSwitcher()
window.show()
sys.exit(app.exec())
