import os
import sys
import time
import shutil
import zipfile
import tempfile
import threading
import datetime
import json
import subprocess
import traceback
import stat
import ctypes
import customtkinter as ctk
from tkinter import filedialog, messagebox

if sys.platform == "win32":
    import winsound

ctk.set_appearance_mode("Dark")

APP_VERSION = "1.1.0"

# --- 1. Вспомогательные функции для работы с путями и скрытием папок ---
def get_base_dir():
    """Получает путь к директории с запущенным exe или py-файлом."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    """Возвращает корректный путь к вшитым ресурсам inside PyInstaller .exe bundle."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = get_base_dir()
    return os.path.join(base_path, relative_path)

def log_message(msg: str):
    """Логирует сообщения в скрытую папку logs."""
    try:
        logs_dir = os.path.join(get_base_dir(), "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
            # Скрываем папку logs в Windows
            if sys.platform == "win32":
                try:
                    FILE_ATTRIBUTE_HIDDEN = 0x02
                    ctypes.windll.kernel32.SetFileAttributesW(logs_dir, FILE_ATTRIBUTE_HIDDEN)
                except Exception:
                    pass

        log_file = os.path.join(logs_dir, f"app_{datetime.date.today().strftime('%Y-%m-%d')}.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass

TRANSLATIONS = {
    "🇷🇺 Русский": {
        "title": "OBS Cyber Backup",
        "status_idle": "● Готов к работе",
        "status_backuping": "● Создание архива...",
        "status_restoring": "● Восстановление данных...",
        "status_done": "● Операция завершена успешно",
        "status_error": "● Произошла ошибка",
        "info_idle": "Выберите компоненты и действие: Бэкап или Восстановление",
        "info_done_backup": "Резервная копия успешно создана и проверена",
        "info_done_restore": "Настройки и плагины OBS успешно восстановлены",
        "btn_backup": "📦 Сделать бэкап OBS",
        "btn_restore": "🔄 Восстановить OBS",
        "btn_transfer": "💻 Перенести OBS на другой ПК",
        "btn_open_folder": "Открыть папку",
        "path_label": "Папка для бэкапов:",
        "path_switch": "Использовать папку Backups рядом с программой",
        "browse_btn": "Обзор...",
        "support_project": "Поддержка проекта",
        "browse_dialog_title": "Выберите папку для сохранения бэкапов",
        "confirm_restore_title": "Подтверждение восстановления",
        "confirm_restore_msg": "Восстановление перезапишет текущие настройки, сцены и плагины OBS Studio.\n\nУбедитесь, что OBS Studio закрыта!\nПродолжить?",
        "err_title": "Ошибка",
        "err_obs_running": "OBS Studio запущен! Пожалуйста, закройте OBS перед продолжением.",
        "err_corrupted_zip": "Выбранный файл не является валидным ZIP-архивом OBS или поврежден.",
        "err_perm_msg": "Не удалось перезаписать файлы в системных папках.\nЗапустите программу от имени Администратора!",
        "err_general_msg": "Ошибка при выполнении операции:\n{}",
        "chk_appdata": "Настройки, сцены и профили (AppData)",
        "chk_programdata": "Плагины OBS (ProgramData)",
        "chk_programfiles": "Плагины OBS (Program Files)",
        "chk_sound": "Звуковые уведомления"
    },
    "🇺🇸 English": {
        "title": "OBS Cyber Backup Utility",
        "status_idle": "● Ready",
        "status_backuping": "● Creating backup...",
        "status_restoring": "● Restoring data...",
        "status_done": "● Operation completed successfully",
        "status_error": "● Error occurred",
        "info_idle": "Select components and action: Backup or Restore",
        "info_done_backup": "Backup successfully created and verified",
        "info_done_restore": "OBS settings and plugins successfully restored",
        "btn_backup": "📦 Create OBS Backup",
        "btn_restore": "🔄 Restore OBS",
        "btn_transfer": "💻 Transfer OBS to another PC",
        "btn_open_folder": "Open Folder",
        "path_label": "Backup folder:",
        "path_switch": "Use Backups folder next to application",
        "browse_btn": "Browse...",
        "support_project": "Support Project",
        "browse_dialog_title": "Select Backup Save Directory",
        "confirm_restore_title": "Confirm Restore",
        "confirm_restore_msg": "Restoring will overwrite current OBS Studio settings, scenes, and plugins.\n\nMake sure OBS Studio is closed!\nContinue?",
        "err_title": "Error",
        "err_obs_running": "OBS Studio is running! Please close OBS before proceeding.",
        "err_corrupted_zip": "The selected file is not a valid OBS ZIP backup or is corrupted.",
        "err_perm_msg": "Failed to overwrite files in system folders.\nPlease run the application as Administrator!",
        "err_general_msg": "Operation failed:\n{}",
        "chk_appdata": "Settings, Scenes & Profiles (AppData)",
        "chk_programdata": "OBS Plugins (ProgramData)",
        "chk_programfiles": "OBS Plugins (Program Files)",
        "chk_sound": "Sound Notifications"
    }
}

DEFAULT_SETTINGS = {
    "backup_folder": "Backups",
    "language": "🇷🇺 Русский",
    "play_sound": True
}

def remove_readonly(func, path, exc_info):
    """Снятие флага Read-Only при ошибках удаления файлов shutil.rmtree"""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def safe_rmtree(path):
    """Безопасное рекурсивное удаление директории"""
    if os.path.exists(path):
        shutil.rmtree(path, onerror=remove_readonly)

def is_obs_running() -> bool:
    if sys.platform == "win32":
        try:
            output = subprocess.check_output('tasklist /FI "IMAGENAME eq obs64.exe"', shell=True, text=True)
            if "obs64.exe" in output:
                return True
            output32 = subprocess.check_output('tasklist /FI "IMAGENAME eq obs32.exe"', shell=True, text=True)
            if "obs32.exe" in output32:
                return True
        except Exception as e:
            log_message(f"Ошибка при проверке запущенного OBS: {e}")
    return False

class ConfigManager:
    def __init__(self, filename="obs_backup_settings.json"):
        self.filepath = os.path.join(get_base_dir(), filename)
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.filepath):
            self.save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, value in DEFAULT_SETTINGS.items():
                    data.setdefault(key, value)
                return data
        except Exception:
            self.save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()

    def save_settings(self, data=None):
        if data is not None:
            self.settings = data
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            log_message(f"Ошибка сохранения настроек: {e}")

    def get(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, error_text, detailed_trace=""):
        super().__init__(parent)
        self.title(title)
        self.geometry("460x320")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0B0C10")
        
        self.detailed_trace = detailed_trace or error_text

        lbl_title = ctk.CTkLabel(self, text="❌ Ошибка операции", font=("Segoe UI", 14, "bold"), text_color="#EF4444")
        lbl_title.pack(pady=(12, 4))

        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 10), fg_color="#14151C", text_color="#F3F4F6", border_width=1, border_color="#232533")
        self.textbox.pack(padx=14, pady=8, fill="both", expand=True)
        self.textbox.insert("1.0", f"{error_text}\n\n--- Подробный лог ---\n{self.detailed_trace}")
        self.textbox.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=14, pady=(0, 12))

        copy_btn = ctk.CTkButton(
            btn_frame, text="📋 Копировать ошибку", font=("Segoe UI", 11, "bold"),
            fg_color="#1E202E", hover_color="#282A3D", command=self.copy_to_clipboard
        )
        copy_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        close_btn = ctk.CTkButton(
            btn_frame, text="Закрыть", font=("Segoe UI", 11, "bold"),
            fg_color="#6366F1", hover_color="#4F46E5", command=self.destroy
        )
        close_btn.pack(side="right", expand=True, fill="x", padx=(4, 0))

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.detailed_trace)
        messagebox.showinfo("Скопировано", "Текст ошибки скопирован в буфер обмена!")

class OBSCyberBackupApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        if sys.platform == "win32":
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"CyberCraft.OBSBackup.App.{APP_VERSION}")
            except Exception:
                pass

        self.processing = False
        self.config = ConfigManager()
        self.current_lang = self.config.get("language")
        
        if self.current_lang not in TRANSLATIONS:
            self.current_lang = "🇷🇺 Русский"

        self.title(self.tr("title"))

        self.appdata_obs = os.path.expandvars(r'%APPDATA%\obs-studio')
        self.programdata_obs_plugins = os.path.expandvars(r'%PROGRAMDATA%\obs-studio\plugins')
        self.programfiles_obs_plugins = os.path.expandvars(r'C:\Program Files\obs-studio\obs-plugins')

        self.CARD_BG = "#14151C"
        self.CARD_BORDER = "#232533"
        self.ACCENT_COLOR = "#6366F1"
        self.ACCENT_HOVER = "#4F46E5"

        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.center_window(520, 690)
        self.setup_ui()

        saved_folder = self.config.get("backup_folder")
        if not os.path.isabs(saved_folder):
            target_dir = os.path.join(get_base_dir(), saved_folder)
        else:
            target_dir = saved_folder

        os.makedirs(target_dir, exist_ok=True)
        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, target_dir)
        self.path_entry.configure(state="readonly")

        log_message("Приложение запущено.")

    def tr(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["🇷🇺 Русский"]).get(key, "")

    def center_window(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        self.configure(fg_color="#0B0C10")

        # Язык
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=14, pady=(8, 2))

        self.lang_optionmenu = ctk.CTkOptionMenu(
            lang_frame, values=list(TRANSLATIONS.keys()), command=self.on_language_change,
            width=130, height=24, font=("Segoe UI", 10, "bold"), fg_color="#1E202E",
            button_color="#282A3D", button_hover_color=self.ACCENT_COLOR,
            dropdown_fg_color="#14151C", dropdown_hover_color=self.ACCENT_COLOR
        )
        self.lang_optionmenu.set(self.current_lang)
        self.lang_optionmenu.pack(side="right")

        # Карточка статуса
        status_card = ctk.CTkFrame(self, fg_color=self.CARD_BG, border_width=1, border_color=self.CARD_BORDER, corner_radius=12)
        status_card.pack(fill="x", padx=14, pady=(6, 6))

        status_box = ctk.CTkFrame(status_card, fg_color="#1E202E", corner_radius=16)
        status_box.pack(pady=(10, 4), padx=10)

        self.status_badge = ctk.CTkLabel(status_box, text=self.tr("status_idle"), font=("Segoe UI", 11, "bold"), text_color="#60A5FA")
        self.status_badge.pack(padx=14, pady=4)

        self.size_label = ctk.CTkLabel(status_card, text="OBS Studio Backup & Restore", font=("Segoe UI", 16, "bold"), text_color="#F3F4F6")
        self.size_label.pack(pady=2)

        self.info_label = ctk.CTkLabel(status_card, text=self.tr("info_idle"), font=("Segoe UI", 10, "bold"), text_color="#9CA3AF")
        self.info_label.pack(pady=(1, 8))

        # Настройки выбора компонентов
        options_card = ctk.CTkFrame(self, fg_color=self.CARD_BG, border_width=1, border_color=self.CARD_BORDER, corner_radius=10)
        options_card.pack(fill="x", padx=14, pady=4, ipady=4)

        opt_title = ctk.CTkLabel(options_card, text="Компоненты для архивации и опции:", font=("Segoe UI", 10, "bold"), text_color="#E5E7EB")
        opt_title.pack(anchor="w", padx=10, pady=(2, 2))

        self.var_appdata = ctk.BooleanVar(value=True)
        self.var_programdata = ctk.BooleanVar(value=True)
        self.var_programfiles = ctk.BooleanVar(value=True)
        self.var_play_sound = ctk.BooleanVar(value=self.config.get("play_sound"))

        self.chk_appdata = ctk.CTkCheckBox(options_card, text=self.tr("chk_appdata"), variable=self.var_appdata, font=("Segoe UI", 10), text_color="#9CA3AF", fg_color=self.ACCENT_COLOR)
        self.chk_appdata.pack(anchor="w", padx=12, pady=2)

        self.chk_programdata = ctk.CTkCheckBox(options_card, text=self.tr("chk_programdata"), variable=self.var_programdata, font=("Segoe UI", 10), text_color="#9CA3AF", fg_color=self.ACCENT_COLOR)
        self.chk_programdata.pack(anchor="w", padx=12, pady=2)

        self.chk_programfiles = ctk.CTkCheckBox(options_card, text=self.tr("chk_programfiles"), variable=self.var_programfiles, font=("Segoe UI", 10), text_color="#9CA3AF", fg_color=self.ACCENT_COLOR)
        self.chk_programfiles.pack(anchor="w", padx=12, pady=2)

        self.chk_sound = ctk.CTkCheckBox(
            options_card, text=self.tr("chk_sound"), variable=self.var_play_sound,
            font=("Segoe UI", 10, "bold"), text_color="#E5E7EB", fg_color=self.ACCENT_COLOR,
            command=self.toggle_sound_setting
        )
        self.chk_sound.pack(anchor="w", padx=12, pady=(4, 2))

        # Пути
        path_card = ctk.CTkFrame(self, fg_color=self.CARD_BG, border_width=1, border_color=self.CARD_BORDER, corner_radius=10)
        path_card.pack(fill="x", padx=14, pady=4, ipady=4)

        self.path_label = ctk.CTkLabel(path_card, text=self.tr("path_label"), font=("Segoe UI", 10, "bold"), text_color="#E5E7EB")
        self.path_label.pack(anchor="w", padx=10, pady=(2, 0))

        self.use_script_dir_var = ctk.BooleanVar(value=True)
        self.same_folder_checkbox = ctk.CTkSwitch(
            path_card, text=self.tr("path_switch"), variable=self.use_script_dir_var,
            font=("Segoe UI", 10), progress_color=self.ACCENT_COLOR, text_color="#9CA3AF", command=self.toggle_path_mode
        )
        self.same_folder_checkbox.pack(anchor="w", padx=10, pady=(2, 4))

        self.path_input_frame = ctk.CTkFrame(path_card, fg_color="transparent")
        self.path_input_frame.pack(fill="x", padx=10, pady=(0, 2))

        self.path_entry = ctk.CTkEntry(self.path_input_frame, height=26, font=("Segoe UI", 10), fg_color="#0B0C10", border_color=self.CARD_BORDER, text_color="#F3F4F6")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.browse_button = ctk.CTkButton(
            self.path_input_frame, text=self.tr("browse_btn"), width=60, height=26, font=("Segoe UI", 10),
            fg_color="#1E202E", hover_color="#282A3D", text_color="#9CA3AF", border_width=1, border_color="#282A3D",
            state="disabled", command=self.browse_folder
        )
        self.browse_button.pack(side="right")

        # Прогресс
        self.progress_bar = ctk.CTkProgressBar(self, height=8, fg_color="#1E202E", progress_color=self.ACCENT_COLOR)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=14, pady=(8, 6), fill="x")

        # Кнопки
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.pack(pady=4, padx=14, fill="x")

        self.backup_button = ctk.CTkButton(
            btn_container, text=self.tr("btn_backup"), font=("Segoe UI", 12, "bold"), height=36, corner_radius=8,
            fg_color=self.ACCENT_COLOR, hover_color=self.ACCENT_HOVER, command=self.start_backup_thread
        )
        self.backup_button.pack(expand=True, fill="x", pady=(0, 4))

        self.transfer_button = ctk.CTkButton(
            btn_container, text=self.tr("btn_transfer"), font=("Segoe UI", 11, "bold"), height=32, corner_radius=6,
            fg_color="#10B981", hover_color="#059669", command=self.start_transfer_wizard
        )
        self.transfer_button.pack(expand=True, fill="x", pady=(0, 6))

        action_row = ctk.CTkFrame(btn_container, fg_color="transparent")
        action_row.pack(fill="x")

        self.restore_button = ctk.CTkButton(
            action_row, text=self.tr("btn_restore"), font=("Segoe UI", 11, "bold"), height=30, corner_radius=6,
            fg_color="#1E202E", hover_color="#282A3D", text_color="#F3F4F6", border_width=1, border_color="#282A3D",
            command=self.start_restore_thread
        )
        self.restore_button.pack(side="left", expand=True, fill="x", padx=(0, 2))

        self.open_folder_button = ctk.CTkButton(
            action_row, text=self.tr("btn_open_folder"), font=("Segoe UI", 11, "bold"), height=30, width=120, corner_radius=6,
            fg_color="#1E202E", hover_color="#282A3D", text_color="#9CA3AF", border_width=1, border_color="#282A3D",
            command=self.open_backup_folder
        )
        self.open_folder_button.pack(side="right", padx=(2, 0))

        # Подвал
        links_frame = ctk.CTkFrame(self, fg_color="transparent")
        links_frame.pack(side="bottom", pady=8)

        self.support_label = ctk.CTkLabel(links_frame, text=self.tr("support_project"), font=("Segoe UI", 9), text_color="#4B5563")
        self.support_label.pack(pady=(0, 2))

        btn_box = ctk.CTkFrame(links_frame, fg_color="transparent")
        btn_box.pack()

        yt_btn = ctk.CTkButton(
            btn_box, text="YouTube", font=("Segoe UI", 10, "bold"), width=85, height=24, corner_radius=6,
            fg_color="#1E202E", hover_color="#282A3D", text_color="#EF4444", border_width=1, border_color="#282A3D",
            command=lambda: os.system("start https://www.youtube.com/channel/UCcGfKjP4XdfkLokNgVOIAyA")
        )
        yt_btn.pack(side="left", padx=2)

        tg_btn = ctk.CTkButton(
            btn_box, text="Telegram", font=("Segoe UI", 10, "bold"), width=85, height=24, corner_radius=6,
            fg_color="#1E202E", hover_color="#282A3D", text_color="#38BDF8", border_width=1, border_color="#282A3D",
            command=lambda: os.system("start https://t.me/CyberCraftLab")
        )
        tg_btn.pack(side="left", padx=2)

        boosty_btn = ctk.CTkButton(
            btn_box, text="Boosty", font=("Segoe UI", 10, "bold"), width=85, height=24, corner_radius=6,
            fg_color="#1E202E", hover_color="#282A3D", text_color="#FB923C", border_width=1, border_color="#282A3D",
            command=lambda: os.system("start https://boosty.to/cyber_craft")
        )
        boosty_btn.pack(side="left", padx=2)

    def toggle_sound_setting(self):
        self.config.set("play_sound", self.var_play_sound.get())

    def play_sound(self, sound_type="success"):
        if not self.var_play_sound.get():
            return

        if sys.platform == "win32":
            if sound_type == "success":
                sound_path = get_resource_path("alert.wav")
                if os.path.exists(sound_path):
                    try:
                        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                        return
                    except Exception:
                        pass
                winsound.PlaySound("SystemNotification", winsound.SND_ALIAS | winsound.SND_ASYNC)
            else:
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)

    def on_language_change(self, new_lang):
        self.current_lang = new_lang
        self.config.set("language", new_lang)
        self.title(self.tr("title"))
        self.status_badge.configure(text=self.tr("status_idle"))
        self.info_label.configure(text=self.tr("info_idle"))
        self.path_label.configure(text=self.tr("path_label"))
        self.same_folder_checkbox.configure(text=self.tr("path_switch"))
        self.browse_button.configure(text=self.tr("browse_btn"))
        self.backup_button.configure(text=self.tr("btn_backup"))
        self.restore_button.configure(text=self.tr("btn_restore"))
        self.transfer_button.configure(text=self.tr("btn_transfer"))
        self.open_folder_button.configure(text=self.tr("btn_open_folder"))
        self.support_label.configure(text=self.tr("support_project"))
        self.chk_appdata.configure(text=self.tr("chk_appdata"))
        self.chk_programdata.configure(text=self.tr("chk_programdata"))
        self.chk_programfiles.configure(text=self.tr("chk_programfiles"))
        self.chk_sound.configure(text=self.tr("chk_sound"))

    def toggle_path_mode(self):
        if self.use_script_dir_var.get():
            backups_dir = os.path.join(get_base_dir(), "Backups")
            os.makedirs(backups_dir, exist_ok=True)
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, backups_dir)
            self.path_entry.configure(state="readonly")
            self.browse_button.configure(state="disabled")
            self.config.set("backup_folder", "Backups")
        else:
            self.browse_button.configure(state="normal")

    def browse_folder(self):
        selected_directory = filedialog.askdirectory(title=self.tr("browse_dialog_title"), initialdir=self.path_entry.get())
        if selected_directory:
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, selected_directory)
            self.path_entry.configure(state="readonly")
            self.config.set("backup_folder", selected_directory)

    def set_ui_lock(self, locked: bool):
        state = "disabled" if locked else "normal"
        self.backup_button.configure(state=state)
        self.restore_button.configure(state=state)
        self.transfer_button.configure(state=state)
        self.same_folder_checkbox.configure(state=state)
        self.chk_appdata.configure(state=state)
        self.chk_programdata.configure(state=state)
        self.chk_programfiles.configure(state=state)
        self.chk_sound.configure(state=state)
        if not self.use_script_dir_var.get():
            self.browse_button.configure(state=state)

    def start_backup_thread(self):
        if self.processing:
            return

        if is_obs_running():
            messagebox.showwarning(self.tr("err_title"), self.tr("err_obs_running"))
            return

        self.processing = True
        self.set_ui_lock(True)
        self.status_badge.configure(text=self.tr("status_backuping"), text_color="#06B6D4")
        self.progress_bar.set(0.1)
        threading.Thread(target=self._backup_worker, daemon=True).start()

    def _backup_worker(self):
        try:
            log_message("Старт процесса бэкапа...")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"OBS_Backup_{timestamp}.zip"
            target_dir = self.path_entry.get()
            os.makedirs(target_dir, exist_ok=True)
            save_path = os.path.join(target_dir, filename)

            files_to_zip = []
            folders_to_process = []

            if self.var_appdata.get():
                folders_to_process.append((self.appdata_obs, "AppData_obs-studio"))
            if self.var_programdata.get():
                folders_to_process.append((self.programdata_obs_plugins, "ProgramData_plugins"))
            if self.var_programfiles.get():
                folders_to_process.append((self.programfiles_obs_plugins, "ProgramFiles_plugins"))

            for folder_path, prefix in folders_to_process:
                if os.path.exists(folder_path):
                    for root_dir, _, files in os.walk(folder_path):
                        for file in files:
                            full_path = os.path.join(root_dir, file)
                            rel_path = os.path.relpath(full_path, folder_path)
                            arcname = os.path.join(prefix, rel_path)
                            files_to_zip.append((full_path, arcname))

            total_files = len(files_to_zip)
            if total_files == 0:
                raise Exception("Не выбраны компоненты или нужные папки OBS Studio не найдены!")

            manifest = {
                "app": "OBS Cyber Backup Utility",
                "version": APP_VERSION,
                "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_files": total_files,
                "appdata_obs": self.var_appdata.get(),
                "programdata_plugins": self.var_programdata.get(),
                "programfiles_plugins": self.var_programfiles.get()
            }

            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr("backup_info.json", json.dumps(manifest, ensure_ascii=False, indent=4))
                for idx, (full_p, arc_n) in enumerate(files_to_zip, start=1):
                    zipf.write(full_p, arc_n)
                    prog = idx / total_files
                    self.after(0, lambda p=prog, i=idx, t=total_files: self._update_progress(p, f"Запись: {i}/{t} файлов"))

            self.after(0, lambda: self._update_progress(0.95, "Проверка ZIP-архива..."))
            with zipfile.ZipFile(save_path, 'r') as zipf:
                if zipf.testzip() is not None:
                    raise Exception("Архив повреждён при создании!")

            file_size_mb = os.path.getsize(save_path) / (1024 * 1024)
            log_message(f"Бэкап создан успешно: {save_path} ({file_size_mb:.2f} MB)")
            self.after(0, lambda: self._on_backup_success(filename, file_size_mb))

        except Exception as e:
            trace_info = traceback.format_exc()
            log_message(f"Ошибка бэкапа: {e}\n{trace_info}")
            self.after(0, lambda: self._on_operation_error(str(e), trace_info))
        finally:
            self.processing = False

    def _update_progress(self, progress, info_text):
        self.progress_bar.set(progress)
        self.info_label.configure(text=info_text, text_color="#06B6D4")

    def _on_backup_success(self, filename, size_mb):
        self.set_ui_lock(False)
        self.progress_bar.set(1.0)
        self.play_sound("success")
        self.status_badge.configure(text=self.tr("status_done"), text_color="#10B981")
        self.info_label.configure(text=f"{filename} ({size_mb:.1f} MB)", text_color="#10B981")

    def start_restore_thread(self):
        if self.processing:
            return

        if is_obs_running():
            messagebox.showwarning(self.tr("err_title"), self.tr("err_obs_running"))
            return

        zip_path = filedialog.askopenfilename(title="Выберите ZIP-архив бэкапа OBS", filetypes=[("ZIP Архив", "*.zip")])
        if not zip_path:
            return

        if not zipfile.is_zipfile(zip_path):
            messagebox.showerror(self.tr("err_title"), self.tr("err_corrupted_zip"))
            return

        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                if "backup_info.json" in zipf.namelist():
                    info_data = json.loads(zipf.read("backup_info.json").decode('utf-8'))
                    msg_info = f"Информация об архиве:\n\nСоздан: {info_data.get('created')}\nФайлов: {info_data.get('total_files')}\nВерсия: {info_data.get('version')}\n\nПродолжить восстановление?"
                else:
                    msg_info = self.tr("confirm_restore_msg")
        except Exception:
            msg_info = self.tr("confirm_restore_msg")

        confirm = messagebox.askyesno(self.tr("confirm_restore_title"), msg_info)
        if not confirm:
            return

        self.processing = True
        self.set_ui_lock(True)
        self.status_badge.configure(text=self.tr("status_restoring"), text_color="#06B6D4")
        self.progress_bar.set(0.1)

        threading.Thread(target=self._restore_worker, args=(zip_path,), daemon=True).start()

    def _restore_worker(self, zip_path):
        rollback_dir = os.path.join(tempfile.gettempdir(), "obs_backup_rollback_tmp")
        try:
            log_message(f"Старт восстановления из {zip_path}...")
            safe_rmtree(rollback_dir)

            if os.path.exists(self.appdata_obs):
                self.after(0, lambda: self._update_progress(0.2, "Создание точки восстановления..."))
                shutil.copytree(self.appdata_obs, rollback_dir)

            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    for member in zipf.infolist():
                        target_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                        if not target_path.startswith(os.path.abspath(temp_dir)):
                            raise Exception(f"Обнаружена угроза безопасности (Zip Slip): {member.filename}")
                        zipf.extract(member, temp_dir)

                self.after(0, lambda: self._update_progress(0.5, "Восстановление AppData..."))
                appdata_src = os.path.join(temp_dir, "AppData_obs-studio")
                if os.path.exists(appdata_src):
                    safe_rmtree(self.appdata_obs)
                    shutil.copytree(appdata_src, self.appdata_obs)

                self.after(0, lambda: self._update_progress(0.7, "Восстановление ProgramData..."))
                programdata_src = os.path.join(temp_dir, "ProgramData_plugins")
                if os.path.exists(programdata_src):
                    os.makedirs(self.programdata_obs_plugins, exist_ok=True)
                    shutil.copytree(programdata_src, self.programdata_obs_plugins, dirs_exist_ok=True)

                self.after(0, lambda: self._update_progress(0.9, "Восстановление Program Files..."))
                programfiles_src = os.path.join(temp_dir, "ProgramFiles_plugins")
                if os.path.exists(programfiles_src):
                    os.makedirs(self.programfiles_obs_plugins, exist_ok=True)
                    shutil.copytree(programfiles_src, self.programfiles_obs_plugins, dirs_exist_ok=True)

            log_message("Восстановление успешно завершено.")
            self.after(0, self._on_restore_success)

        except PermissionError as pe:
            self._execute_rollback(rollback_dir)
            trace_info = traceback.format_exc()
            log_message(f"PermissionError при восстановлении: {pe}\n{trace_info}")
            self.after(0, lambda: self._on_operation_error(self.tr("err_perm_msg"), trace_info))
        except Exception as e:
            self._execute_rollback(rollback_dir)
            trace_info = traceback.format_exc()
            log_message(f"Ошибка при восстановлении: {e}\n{trace_info}")
            self.after(0, lambda: self._on_operation_error(str(e), trace_info))
        finally:
            safe_rmtree(rollback_dir)
            self.processing = False

    def _execute_rollback(self, rollback_dir):
        if os.path.exists(rollback_dir):
            try:
                log_message("Запуск Rollback: Откат изменений к исходному состоянию...")
                safe_rmtree(self.appdata_obs)
                shutil.copytree(rollback_dir, self.appdata_obs)
            except Exception as e:
                log_message(f"Критическая ошибка Rollback: {e}")

    def _on_restore_success(self):
        self.set_ui_lock(False)
        self.progress_bar.set(1.0)
        self.play_sound("success")
        self.status_badge.configure(text=self.tr("status_done"), text_color="#10B981")
        self.info_label.configure(text=self.tr("info_done_restore"), text_color="#10B981")

    def _on_operation_error(self, err_msg, detailed_trace=""):
        self.set_ui_lock(False)
        self.play_sound("error")
        self.status_badge.configure(text=self.tr("status_error"), text_color="#EF4444")
        self.info_label.configure(text=self.tr("err_title"), text_color="#EF4444")
        self.progress_bar.set(0)
        ErrorDialog(self, self.tr("err_title"), err_msg, detailed_trace)

    def start_transfer_wizard(self):
        messagebox.showinfo("Перенос OBS", "Инструкция по переносу на другой ПК:\n\n1. Нажмите 'Сделать бэкап OBS' на этом ПК.\n2. Скопируйте созданный ZIP-архив на флешку.\n3. Запустите данную утилиту на новом ПК.\n4. Нажмите 'Восстановить OBS' и выберите файл архива с флешки.")

    def open_backup_folder(self):
        target_dir = self.path_entry.get()
        if os.path.exists(target_dir):
            if sys.platform == "win32":
                os.startfile(target_dir)
            else:
                os.system(f'xdg-open "{target_dir}"')

if __name__ == "__main__":
    app = OBSCyberBackupApp()
    app.mainloop()