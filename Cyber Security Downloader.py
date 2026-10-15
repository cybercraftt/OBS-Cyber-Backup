import os
import sys
import time
import datetime
import threading
import ssl
import urllib.request
import urllib.parse
import hashlib
import json
import re
import subprocess
import zipfile
import webbrowser
import customtkinter as ctk
from tkinter import filedialog, messagebox

if sys.platform == "win32":
    import winsound
    import ctypes

ctk.set_appearance_mode("Dark")

TRANSLATIONS = {
    "🇷🇺 Русский": {
        "status_checking": "● Проверка состояния...",
        "status_local": "● Локальный файл от {}",
        "status_not_found": "● Файл не найден",
        "status_update_available": "● ДОСТУПНА НОВАЯ ВЕРСИЯ!",
        "status_actual": "● Установлена актуальная версия",
        "status_connecting": "● Соединение с сервером...",
        "status_downloading": "● Загрузка новой версии...",
        "status_canceled": "● Отменено пользователем",
        "status_error": "● Ошибка загрузки",
        "size_def": "Размер: Определение...",
        "size_local": "Локально: {:.2f} МБ",
        "size_approx": "Размер: ~{:.1f} МБ",
        "info_checking_bases": "Проверка свежих баз на сервере...",
        "info_new_base": "На сервере появилась свежая база ({:.1f} МБ)",
        "info_actual_base": "Ваша версия совпадает с последней базой на сервере",
        "info_connecting": "Подключение к серверу...",
        "info_download_speed": "{:.2f} МБ/с • осталось ~{} сек",
        "info_updated_signatures": "База данных сигнатур обновлена",
        "info_stopped": "Загрузка остановлена",
        "info_failed": "Не удалось обновить утилиту",
        "btn_download": "Скачать {}",
        "btn_download_again": "Скачать заново",
        "btn_update": "Обновить {}",
        "btn_redownload": "Перекачать файл",
        "btn_cancel": "Отменить загрузку",
        "btn_canceling": "Отмена...",
        "btn_run": "Запустить утилиту",
        "btn_open_folder": "Открыть папку",
        "path_label": "Папка для сохранения:",
        "path_switch": "Использовать папку Downloads рядом с программой",
        "sound_switch": "Звуковое уведомление по окончании загрузки",
        "browse_btn": "Обзор...",
        "support_project": "Поддержка проекта",
        "browse_dialog_title": "Выберите папку для сохранения",
        "err_download_title": "Ошибка загрузки",
        "err_download_msg": "Не удалось безопасно скачать файл:\n{}",
        "err_run_title": "Ошибка",
        "err_run_msg": "Не удалось запустить файл:\n{}"
    },
    "🇺🇸 English": {
        "status_checking": "● Checking status...",
        "status_local": "● Local file from {}",
        "status_not_found": "● File not found",
        "status_update_available": "● NEW VERSION AVAILABLE!",
        "status_actual": "● Up to date",
        "status_connecting": "● Connecting to server...",
        "status_downloading": "● Downloading new version...",
        "status_canceled": "● Canceled by user",
        "status_error": "● Download error",
        "size_def": "Size: Detecting...",
        "size_local": "Local: {:.2f} MB",
        "size_approx": "Size: ~{:.1f} MB",
        "info_checking_bases": "Checking server for fresh updates...",
        "info_new_base": "New update available on server ({:.1f} MB)",
        "info_actual_base": "Your version matches the latest server update",
        "info_connecting": "Connecting to server...",
        "info_download_speed": "{:.2f} MB/s • ~{} sec remaining",
        "info_updated_signatures": "Database updated",
        "info_stopped": "Download stopped",
        "info_failed": "Failed to update utility",
        "btn_download": "Download {}",
        "btn_download_again": "Redownload",
        "btn_update": "Update {}",
        "btn_redownload": "Redownload file",
        "btn_cancel": "Cancel download",
        "btn_canceling": "Canceling...",
        "btn_run": "Run Utility",
        "btn_open_folder": "Open Folder",
        "path_label": "Save folder:",
        "path_switch": "Use Downloads folder next to application",
        "sound_switch": "Play sound on completion",
        "browse_btn": "Browse...",
        "support_project": "Support Project",
        "browse_dialog_title": "Select Save Directory",
        "err_download_title": "Download Error",
        "err_download_msg": "Failed to safely download file:\n{}",
        "err_run_title": "Error",
        "err_run_msg": "Failed to run file:\n{}"
    },
    "🇪🇸 Español": {
        "status_checking": "● Comprobando estado...",
        "status_local": "● Archivo local del {}",
        "status_not_found": "● Archivo no encontrado",
        "status_update_available": "● ¡NUEVA VERSIÓN DISPONIBLE!",
        "status_actual": "● Actualizado",
        "status_connecting": "● Conectando al servidor...",
        "status_downloading": "● Descargando nueva versión...",
        "status_canceled": "● Cancelado por el usuario",
        "status_error": "● Error de descarga",
        "size_def": "Tamaño: Detectando...",
        "size_local": "Local: {:.2f} MB",
        "size_approx": "Tamaño: ~{:.1f} MB",
        "info_checking_bases": "Buscando actualizaciones en el servidor...",
        "info_new_base": "Nueva actualización disponible ({:.1f} MB)",
        "info_actual_base": "Tu versión coincide con la última del servidor",
        "info_connecting": "Conectando al servidor...",
        "info_download_speed": "{:.2f} MB/s • ~{} seg restantes",
        "info_updated_signatures": "Base de datos actualizada",
        "info_stopped": "Descarga detenida",
        "info_failed": "Error al actualizar la utilidad",
        "btn_download": "Descargar {}",
        "btn_download_again": "Descargar de nuevo",
        "btn_update": "Actualizar {}",
        "btn_redownload": "Volver a descargar",
        "btn_cancel": "Cancelar descarga",
        "btn_canceling": "Cancelando...",
        "btn_run": "Ejecutar utilidad",
        "btn_open_folder": "Abrir carpeta",
        "path_label": "Carpeta de guardado:",
        "path_switch": "Usar carpeta Downloads junto a la aplicación",
        "sound_switch": "Sonido al finalizar la descarga",
        "browse_btn": "Examinar...",
        "support_project": "Apoyar el proyecto",
        "browse_dialog_title": "Seleccionar carpeta de guardado",
        "err_download_title": "Error de descarga",
        "err_download_msg": "No se pudo descargar el archivo de forma segura:\n{}",
        "err_run_title": "Error",
        "err_run_msg": "No se pudo ejecutar el archivo:\n{}"
    },
    "🇩🇪 Deutsch": {
        "status_checking": "● Status wird geprüft...",
        "status_local": "● Lokale Datei vom {}",
        "status_not_found": "● Datei nicht gefunden",
        "status_update_available": "● NEUE VERSION VERFÜGBAR!",
        "status_actual": "● Auf dem neuesten Stand",
        "status_connecting": "● Verbindung zum Server...",
        "status_downloading": "● Neue Version wird heruntergeladen...",
        "status_canceled": "● Vom Benutzer abgebrochen",
        "status_error": "● Download-Fehler",
        "size_def": "Größe: Ermittlung...",
        "size_local": "Lokal: {:.2f} MB",
        "size_approx": "Größe: ~{:.1f} MB",
        "info_checking_bases": "Überprüfe Server auf Updates...",
        "info_new_base": "Neues Update verfügbar ({:.1f} MB)",
        "info_actual_base": "Ihre Version ist aktuell",
        "info_connecting": "Verbindung zum Server...",
        "info_download_speed": "{:.2f} MB/s • ~{} Sek. verbleibend",
        "info_updated_signatures": "Datenbank aktualisiert",
        "info_stopped": "Download angehalten",
        "info_failed": "Aktualisierung fehlgeschlagen",
        "btn_download": "Herunterladen {}",
        "btn_download_again": "Erneut herunterladen",
        "btn_update": "Aktualisieren {}",
        "btn_redownload": "Datei erneut herunterladen",
        "btn_cancel": "Download abbrechen",
        "btn_canceling": "Abbrechen...",
        "btn_run": "Utility starten",
        "btn_open_folder": "Ordner öffnen",
        "path_label": "Speicherpfad:",
        "path_switch": "Downloads-Ordner neben dem Programm verwenden",
        "sound_switch": "Ton bei Fertigstellung abspielen",
        "browse_btn": "Durchsuchen...",
        "support_project": "Projekt unterstützen",
        "browse_dialog_title": "Speicherordner auswählen",
        "err_download_title": "Download-Fehler",
        "err_download_msg": "Datei konnte nicht sicher heruntergeladen werden:\n{}",
        "err_run_title": "Fehler",
        "err_run_msg": "Datei konnte nicht gestartet werden:\n{}"
    },
    "🇫🇷 Français": {
        "status_checking": "● Vérification du statut...",
        "status_local": "● Fichier local du {}",
        "status_not_found": "● Fichier non trouvé",
        "status_update_available": "● NOUVELLE VERSION DISPONIBLE !",
        "status_actual": "● À jour",
        "status_connecting": "● Connexion au serveur...",
        "status_downloading": "● Téléchargement de la nouvelle version...",
        "status_canceled": "● Annulé par l'utilisateur",
        "status_error": "● Erreur de téléchargement",
        "size_def": "Taille : Détection...",
        "size_local": "Local : {:.2f} Mo",
        "size_approx": "Taille : ~{:.1f} Mo",
        "info_checking_bases": "Vérification des mises à jour...",
        "info_new_base": "Mise à jour disponible ({:.1f} Mo)",
        "info_actual_base": "Votre version est à jour",
        "info_connecting": "Connexion au serveur...",
        "info_download_speed": "{:.2f} Mo/s • ~{} sec restantes",
        "info_updated_signatures": "Base de données mise à jour",
        "info_stopped": "Téléchargement arrêté",
        "info_failed": "Échec de la mise à jour",
        "btn_download": "Télécharger {}",
        "btn_download_again": "Télécharger à nouveau",
        "btn_update": "Mettre à jour {}",
        "btn_redownload": "Re-télécharger le fichier",
        "btn_cancel": "Annuler le téléchargement",
        "btn_canceling": "Annulation...",
        "btn_run": "Lancer l'utilitaire",
        "btn_open_folder": "Ouvrir le dossier",
        "path_label": "Dossier d'enregistrement :",
        "path_switch": "Utiliser le dossier Downloads à côté du programme",
        "sound_switch": "Signal sonore à la fin du téléchargement",
        "browse_btn": "Parcourir...",
        "support_project": "Soutenir le projet",
        "browse_dialog_title": "Sélectionner le dossier d'enregistrement",
        "err_download_title": "Erreur de téléchargement",
        "err_download_msg": "Impossible de télécharger le fichier en toute sécurité :\n{}",
        "err_run_title": "Erreur",
        "err_run_msg": "Impossible de lancer le fichier :\n{}"
    },
    "🇨🇳 中文": {
        "status_checking": "● 正在检查状态...",
        "status_local": "● 本地文件来自 {}",
        "status_not_found": "● 未找到文件",
        "status_update_available": "● 有新版本可用！",
        "status_actual": "● 已是最新版本",
        "status_connecting": "● 正在连接服务器...",
        "status_downloading": "● 正在下载新版本...",
        "status_canceled": "● 用户已取消",
        "status_error": "● 下载错误",
        "size_def": "大小: 正在检测...",
        "size_local": "本地文件: {:.2f} MB",
        "size_approx": "大小: ~{:.1f} MB",
        "info_checking_bases": "正在检查服务器是否有更新...",
        "info_new_base": "服务器上有新更新 ({:.1f} MB)",
        "info_actual_base": "您的版本与服务器最新版本一致",
        "info_connecting": "正在连接到服务器...",
        "info_download_speed": "{:.2f} MB/s • 剩余 ~{} 秒",
        "info_updated_signatures": "数据库已更新",
        "info_stopped": "下载已停止",
        "info_failed": "更新工具失败",
        "btn_download": "下载 {}",
        "btn_download_again": "重新下载",
        "btn_update": "更新 {}",
        "btn_redownload": "重新下载文件",
        "btn_cancel": "取消下载",
        "btn_canceling": "正在取消...",
        "btn_run": "运行工具",
        "btn_open_folder": "打开文件夹",
        "path_label": "保存路径:",
        "path_switch": "使用程序旁边的 Downloads 文件夹",
        "sound_switch": "下载完成时播放提示音",
        "browse_btn": "浏览...",
        "support_project": "支持项目",
        "browse_dialog_title": "选择保存文件夹",
        "err_download_title": "下载错误",
        "err_download_msg": "无法安全下载文件:\n{}",
        "err_run_title": "错误",
        "err_run_msg": "无法运行文件:\n{}"
    },
    "🇵🇹 Português": {
        "status_checking": "● Verificando status...",
        "status_local": "● Arquivo local de {}",
        "status_not_found": "● Arquivo não encontrado",
        "status_update_available": "● NOVA VERSÃO DISPONÍVEL!",
        "status_actual": "● Atualizado",
        "status_connecting": "● Conectando ao servidor...",
        "status_downloading": "● Baixando nova versão...",
        "status_canceled": "● Cancelado pelo usuário",
        "status_error": "● Erro de download",
        "size_def": "Tamanho: Detectando...",
        "size_local": "Local: {:.2f} MB",
        "size_approx": "Tamanho: ~{:.1f} MB",
        "info_checking_bases": "Verificando atualizações no servidor...",
        "info_new_base": "Nova atualização disponível ({:.1f} MB)",
        "info_actual_base": "Sua versão corresponde à mais recente",
        "info_connecting": "Conectando ao servidor...",
        "info_download_speed": "{:.2f} MB/s • ~{} seg restantes",
        "info_updated_signatures": "Banco de dados atualizado",
        "info_stopped": "Download interrompido",
        "info_failed": "Falha ao atualizar o utilitário",
        "btn_download": "Baixar {}",
        "btn_download_again": "Baixar novamente",
        "btn_update": "Atualizar {}",
        "btn_redownload": "Rebaixar arquivo",
        "btn_cancel": "Cancelar download",
        "btn_canceling": "Cancelando...",
        "btn_run": "Executar utilitário",
        "btn_open_folder": "Abrir pasta",
        "path_label": "Pasta de destino:",
        "path_switch": "Usar pasta Downloads junto ao aplicativo",
        "sound_switch": "Tocar som ao concluir o download",
        "browse_btn": "Procurar...",
        "support_project": "Apoiar o projeto",
        "browse_dialog_title": "Selecionar pasta de destino",
        "err_download_title": "Erro de download",
        "err_download_msg": "Não foi possível baixar o arquivo com segurança:\n{}",
        "err_run_title": "Erro",
        "err_run_msg": "Não foi possível executar o arquivo:\n{}"
    },
    "🇯🇵 日本語": {
        "status_checking": "● ステータスを確認中...",
        "status_local": "● ローカルファイル ({})",
        "status_not_found": "● ファイルが見つかりません",
        "status_update_available": "● 新しいバージョンが利用可能です！",
        "status_actual": "● 最新の状態です",
        "status_connecting": "● サーバーに接続中...",
        "status_downloading": "● 新しいバージョンをダウンロード中...",
        "status_canceled": "● ユーザーによってキャンセルされました",
        "status_error": "● ダウンロードエラー",
        "size_def": "サイズ: 検出中...",
        "size_local": "ローカル: {:.2f} MB",
        "size_approx": "サイズ: ~{:.1f} MB",
        "info_checking_bases": "サーバーで最新の更新を確認中...",
        "info_new_base": "サーバーに新しい更新があります ({:.1f} MB)",
        "info_actual_base": "お使いのバージョンは最新です",
        "info_connecting": "サーバーに接続中...",
        "info_download_speed": "{:.2f} MB/s • 残り ~{} 秒",
        "info_updated_signatures": "データベースが更新されました",
        "info_stopped": "ダウンロードが停止しました",
        "info_failed": "ユーティリティの更新に失敗しました",
        "btn_download": "ダウンロード {}",
        "btn_download_again": "再ダウンロード",
        "btn_update": "更新 {}",
        "btn_redownload": "ファイルを再ダウンロード",
        "btn_cancel": "ダウンロードをキャンセル",
        "btn_canceling": "キャンセル中...",
        "btn_run": "ユーティリティを実行",
        "btn_open_folder": "フォルダを開く",
        "path_label": "保存先フォルダ:",
        "path_switch": "アプリと同じ場所の Downloads フォルダを使用",
        "sound_switch": "ダウンロード完了時に an 音声を再生",
        "browse_btn": "参照...",
        "support_project": "プロジェクトを支援",
        "browse_dialog_title": "保存先フォルダを選択",
        "err_download_title": "ダウンロードエラー",
        "err_download_msg": "ファイルを安全にダウンロードできませんでした:\n{}",
        "err_run_title": "エラー",
        "err_run_msg": "ファイルを実行できませんでした:\n{}"
    }
}

UTILITIES = {
    "Dr.Web CureIt!": {
        "url": "https://free.drweb.ru/download+cureit+free/",
        "download_url": "https://free.drweb.ru/download+cureit/gr/?lng=ru",
        "referer": "https://free.drweb.ru/download+cureit+free/",
        "default_filename": "cureit.exe",
        "is_archive": False,
        "description": {
            "🇷🇺 Русский": "Автономный антивирусный сканер",
            "🇺🇸 English": "Standalone antivirus scanner",
            "🇪🇸 Español": "Escáner antivirus independiente",
            "🇩🇪 Deutsch": "Eigenständiger Antiviren-Scanner",
            "🇫🇷 Français": "Scanner antivirus autonome",
            "🇨🇳 中文": "独立杀毒扫描工具",
            "🇵🇹 Português": "Escaneador antivírus autônomo",
            "🇯🇵 日本語": "スタンドアロン型ウイルス対策スキャナー"
        }
    },
    "AdwCleaner": {
        "url": "https://www.malwarebytes.com/adwcleaner",
        "download_url": "https://adwcleaner.malwarebytes.com/adwcleaner?channel=release",
        "referer": "https://www.malwarebytes.com/",
        "default_filename": "adwcleaner.exe",
        "is_archive": False,
        "description": {
            "🇷🇺 Русский": "Удаление Adware, PUP и браузерных плагинов",
            "🇺🇸 English": "Removes Adware, PUPs, and toolbar plugins",
            "🇪🇸 Español": "Elimina Adware, PUPs y complementos del navegador",
            "🇩🇪 Deutsch": "Entfernt Adware, PUPs und Browser-Plugins",
            "🇫🇷 Français": "Supprime les logiciels publicitaires, PUP et extensions",
            "🇨🇳 中文": "清除广告软件、PUP及浏览器插件",
            "🇵🇹 Português": "Remove Adware, PUPs e plugins de navegador",
            "🇯🇵 日本語": "アドウェア、PUP、ブラウザプラグインの削除"
        }
    },
    "MinerSearch": {
        "url": "https://blendlog.github.io/",
        "download_url": "https://github.com/BlendLog/MinerSearch/releases/download/v1.4.9.2/MinerSearch_v1.4.9.2.zip",
        "referer": "https://blendlog.github.io/",
        "default_filename": "MinerSearch_v1.4.9.2.exe",
        "archive_filename": "MinerSearch_v1.4.9.2.zip",
        "is_archive": True,
        "description": {
            "🇷🇺 Русский": "Поиск и удаление скрытых майнеров",
            "🇺🇸 English": "Detect and remove hidden crypto miners",
            "🇪🇸 Español": "Detecta y elimina mineros de criptomonnadas ocultos",
            "🇩🇪 Deutsch": "Erkennt und entfernt versteckte Crypto-Miner",
            "🇫🇷 Français": "Détecte et supprime les mineurs de cryptomonnaie cachés",
            "🇨🇳 中文": "检测并清除隐藏的加密货币挖矿程序",
            "🇵🇹 Português": "Detecta e remove mineradores de criptomoedas ocultos",
            "🇯🇵 日本語": "非表示の暗号通貨マイナーの検出と削除"
        }
    }
}

DEFAULT_SETTINGS = {
    "last_utility": "Dr.Web CureIt!",
    "downloads_folder": "Downloads",
    "language": "🇷🇺 Русский",
    "sound_enabled": True
}

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = get_base_dir()
    return os.path.join(base_path, relative_path)

def parse_content_disposition(header):
    if not header:
        return None
    utf8_match = re.search(r"filename\*\s*=\s*UTF-8''([^;]+)", header, re.IGNORECASE)
    if utf8_match:
        return urllib.parse.unquote(utf8_match.group(1))
    std_match = re.search(r'filename\s*=\s*"?([^";]+)"?', header, re.IGNORECASE)
    if std_match:
        return std_match.group(1)
    return None

class ConfigManager:
    def __init__(self, filename="settings.json"):
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
            print(f"Ошибка сохранения settings.json: {e}")

    def get(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

class CyberDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        if sys.platform == "win32":
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CyberCraft.UtilityDownloader.App.2.4")
            except Exception:
                pass

        self.title("Cyber Security Downloader")
        self.downloading = False
        self.cancel_requested = False
        self.downloaded_file_path = None
        self.remote_file_size = 0
        self.is_update_available = False

        self.config = ConfigManager("settings.json")
        self.selected_utility = self.config.get("last_utility")
        if self.selected_utility not in UTILITIES:
            self.selected_utility = "Dr.Web CureIt!"

        self.current_lang = self.config.get("language")

        if self.current_lang not in TRANSLATIONS:
            for k in TRANSLATIONS.keys():
                if self.current_lang in k:
                    self.current_lang = k
                    break
            else:
                self.current_lang = "🇷🇺 Русский"

        self.CARD_BG = "#14151C"
        self.CARD_BORDER = "#232533"
        self.ACCENT_COLOR = "#6366F1"
        self.ACCENT_HOVER = "#4F46E5"
        self.UPDATE_COLOR = "#10B981"
        self.UPDATE_HOVER = "#059669"
        self.CANCEL_COLOR = "#EF4444"
        self.CANCEL_HOVER = "#DC2626"

        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.center_window(490, 615)
        self.setup_ui()

        saved_folder = self.config.get("downloads_folder")
        if not os.path.isabs(saved_folder):
            target_dir = os.path.join(get_base_dir(), saved_folder)
        else:
            target_dir = saved_folder

        os.makedirs(target_dir, exist_ok=True)
        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, target_dir)
        self.path_entry.configure(state="readonly")

        self.check_existing_file()
        self.check_remote_updates_async()

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

        # Переключатель языка
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=14, pady=(8, 2))

        self.lang_optionmenu = ctk.CTkOptionMenu(
            lang_frame,
            values=list(TRANSLATIONS.keys()),
            command=self.on_language_change,
            width=130,
            height=24,
            font=("Segoe UI", 10, "bold"),
            fg_color="#1E202E",
            button_color="#282A3D",
            button_hover_color=self.ACCENT_COLOR,
            dropdown_fg_color="#14151C",
            dropdown_hover_color=self.ACCENT_COLOR
        )
        self.lang_optionmenu.set(self.current_lang)
        self.lang_optionmenu.pack(side="right")

        # Выбор утилиты
        selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        selector_frame.pack(fill="x", padx=14, pady=(4, 4))

        self.util_selector = ctk.CTkSegmentedButton(
            selector_frame,
            values=list(UTILITIES.keys()),
            selected_color=self.ACCENT_COLOR,
            unselected_color="#1E202E",
            unselected_hover_color="#282A3D",
            text_color="#F3F4F6",
            font=("Segoe UI", 11, "bold"),
            command=self.on_utility_change
        )
        self.util_selector.set(self.selected_utility)
        self.util_selector.pack(fill="x")

        # Карточка статуса
        status_card = ctk.CTkFrame(
            self, fg_color=self.CARD_BG, border_width=1, border_color=self.CARD_BORDER, corner_radius=12
        )
        status_card.pack(fill="x", padx=14, pady=(4, 6))

        status_box = ctk.CTkFrame(status_card, fg_color="#1E202E", corner_radius=16)
        status_box.pack(pady=(8, 2), padx=10)

        self.status_badge = ctk.CTkLabel(
            status_box, text=self.tr("status_checking"), font=("Segoe UI", 11, "bold"), text_color="#9CA3AF"
        )
        self.status_badge.pack(padx=12, pady=3)

        self.size_label = ctk.CTkLabel(
            status_card, text=self.tr("size_def"), font=("Segoe UI", 20, "bold"), text_color="#F3F4F6"
        )
        self.size_label.pack(pady=0)

        self.info_label = ctk.CTkLabel(
            status_card, text=UTILITIES[self.selected_utility]["description"].get(self.current_lang, ""), font=("Segoe UI", 10, "bold"), text_color="#6B7280"
        )
        self.info_label.pack(pady=(1, 6))

        # Настройка папки и звука
        settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        settings_frame.pack(padx=14, fill="x", pady=0)

        path_card = ctk.CTkFrame(
            settings_frame, fg_color=self.CARD_BG, border_width=1, border_color=self.CARD_BORDER, corner_radius=10
        )
        path_card.pack(fill="x", pady=2, ipady=2, ipadx=6)

        self.path_label = ctk.CTkLabel(
            path_card, text=self.tr("path_label"), font=("Segoe UI", 11, "bold"), text_color="#E5E7EB"
        )
        self.path_label.pack(anchor="w", padx=6, pady=(2, 0))

        self.use_script_dir_var = ctk.BooleanVar(value=True)
        self.same_folder_checkbox = ctk.CTkSwitch(
            path_card,
            text=self.tr("path_switch"),
            variable=self.use_script_dir_var,
            font=("Segoe UI", 10),
            progress_color=self.ACCENT_COLOR,
            text_color="#9CA3AF",
            command=self.toggle_path_mode
        )
        self.same_folder_checkbox.pack(anchor="w", padx=6, pady=(1, 2))

        self.sound_enabled_var = ctk.BooleanVar(value=self.config.get("sound_enabled"))
        self.sound_checkbox = ctk.CTkSwitch(
            path_card,
            text=self.tr("sound_switch"),
            variable=self.sound_enabled_var,
            font=("Segoe UI", 10),
            progress_color=self.ACCENT_COLOR,
            text_color="#9CA3AF",
            command=self.toggle_sound_mode
        )
        self.sound_checkbox.pack(anchor="w", padx=6, pady=(1, 4))

        self.path_input_frame = ctk.CTkFrame(path_card, fg_color="transparent")
        self.path_input_frame.pack(fill="x", padx=6, pady=(0, 2))

        self.path_entry = ctk.CTkEntry(
            self.path_input_frame,
            height=26,
            font=("Segoe UI", 10),
            fg_color="#0B0C10",
            border_color=self.CARD_BORDER,
            text_color="#F3F4F6"
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.browse_button = ctk.CTkButton(
            self.path_input_frame,
            text=self.tr("browse_btn"),
            width=60,
            height=26,
            font=("Segoe UI", 10),
            fg_color="#1E202E",
            hover_color="#282A3D",
            text_color="#9CA3AF",
            border_width=1,
            border_color="#282A3D",
            state="disabled",
            command=self.browse_folder
        )
        self.browse_button.pack(side="right")

        # Прогресс-бар
        self.progress_bar = ctk.CTkProgressBar(
            self, height=8, fg_color="#1E202E", progress_color=self.ACCENT_COLOR
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=14, pady=(8, 4), fill="x")

        # Кнопки действия
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.pack(pady=2, padx=14, fill="x")

        self.download_button = ctk.CTkButton(
            btn_container,
            text=self.tr("btn_download").format(self.selected_utility),
            font=("Segoe UI", 12, "bold"),
            height=34,
            corner_radius=8,
            fg_color=self.ACCENT_COLOR,
            hover_color=self.ACCENT_HOVER,
            command=self.handle_download_click
        )
        self.download_button.pack(expand=True, fill="x", pady=(0, 4))

        action_row = ctk.CTkFrame(btn_container, fg_color="transparent")
        action_row.pack(fill="x")

        self.action_button = ctk.CTkButton(
            action_row,
            text=self.tr("btn_run"),
            font=("Segoe UI", 11, "bold"),
            height=28,
            corner_radius=6,
            fg_color="#1E202E",
            hover_color="#282A3D",
            text_color="#9CA3AF",
            border_width=1,
            border_color="#282A3D",
            state="disabled",
            command=self.run_downloaded_file
        )
        self.action_button.pack(side="left", expand=True, fill="x", padx=(0, 2))

        self.open_folder_button = ctk.CTkButton(
            action_row,
            text=self.tr("btn_open_folder"),
            font=("Segoe UI", 11, "bold"),
            height=28,
            width=110,
            corner_radius=6,
            fg_color="#1E202E",
            hover_color="#282A3D",
            text_color="#9CA3AF",
            border_width=1,
            border_color="#282A3D",
            command=self.open_download_folder
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
            command=lambda: webbrowser.open("https://www.youtube.com/channel/UCcGfKjP4XdfkLokNgVOIAyA")
        )
        yt_btn.pack(side="left", padx=2)

        tg_btn = ctk.CTkButton(
            btn_box, text="Telegram", font=("Segoe UI", 10, "bold"), width=85, height=24, corner_radius=6,
            fg_color="#1E202E", hover_color="#282A3D", text_color="#38BDF8", border_width=1, border_color="#282A3D",
            command=lambda: webbrowser.open("https://t.me/CyberCraftLab")
        )
        tg_btn.pack(side="left", padx=2)

        boosty_btn = ctk.CTkButton(
            btn_box, text="Boosty", font=("Segoe UI", 10, "bold"), width=85, height=24, corner_radius=6,
            fg_color="#1E202E", hover_color="#282A3D", text_color="#FB923C", border_width=1, border_color="#282A3D",
            command=lambda: webbrowser.open("https://boosty.to/dufna")
        )
        boosty_btn.pack(side="left", padx=2)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_language_change(self, new_lang):
        self.current_lang = new_lang
        self.config.set("language", new_lang)
        self.path_label.configure(text=self.tr("path_label"))
        self.same_folder_checkbox.configure(text=self.tr("path_switch"))
        self.sound_checkbox.configure(text=self.tr("sound_switch"))
        self.browse_button.configure(text=self.tr("browse_btn"))
        self.action_button.configure(text=self.tr("btn_run"))
        self.open_folder_button.configure(text=self.tr("btn_open_folder"))
        self.support_label.configure(text=self.tr("support_project"))
        self.check_existing_file()
        self.check_remote_updates_async()

    def check_existing_file(self):
        util_info = UTILITIES[self.selected_utility]
        target_dir = self.path_entry.get()
        
        found_file = None
        if os.path.exists(target_dir):
            if util_info.get("is_archive", False):
                subfolder = os.path.join(target_dir, self.selected_utility)
                if os.path.exists(subfolder):
                    for f in os.listdir(subfolder):
                        if f.lower().endswith(".exe"):
                            found_file = os.path.join(subfolder, f)
                            break
            elif self.selected_utility == "Dr.Web CureIt!":
                for f in os.listdir(target_dir):
                    if f.lower().endswith(".exe") and ("cureit" in f.lower() or f.lower().startswith("drweb")):
                        found_file = os.path.join(target_dir, f)
                        break
            else:
                default_path = os.path.join(target_dir, util_info["default_filename"])
                if os.path.exists(default_path):
                    found_file = default_path

        if found_file and os.path.exists(found_file):
            self.downloaded_file_path = found_file
            file_mtime = os.path.getmtime(found_file)
            time_str = datetime.datetime.fromtimestamp(file_mtime).strftime("%d.%m %H:%M")
            file_size_mb = os.path.getsize(found_file) / (1024 * 1024)

            self.status_badge.configure(text=self.tr("status_local").format(time_str), text_color="#60A5FA")
            self.size_label.configure(text=self.tr("size_local").format(file_size_mb))
            self.info_label.configure(text=self.tr("info_checking_bases"), text_color="#9CA3AF")
            self.download_button.configure(
                text=self.tr("btn_download_again"),
                fg_color=self.ACCENT_COLOR,
                hover_color=self.ACCENT_HOVER
            )
            self.action_button.configure(state="normal")
            self.progress_bar.set(1.0)
        else:
            self.downloaded_file_path = None
            self.is_update_available = False
            self.status_badge.configure(text=self.tr("status_not_found"), text_color="#9CA3AF")
            self.size_label.configure(text=self.tr("size_def"))
            self.info_label.configure(text=util_info["description"].get(self.current_lang, ""), text_color="#6B7280")
            self.download_button.configure(
                text=self.tr("btn_download").format(self.selected_utility),
                fg_color=self.ACCENT_COLOR,
                hover_color=self.ACCENT_HOVER
            )
            self.action_button.configure(state="disabled")
            self.progress_bar.set(0)

    def check_remote_updates_async(self):
        threading.Thread(target=self._check_remote_worker, daemon=True).start()

    def _check_remote_worker(self):
        util_info = UTILITIES[self.selected_utility]
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(
                util_info["download_url"],
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Referer': util_info["referer"]
                },
                method='HEAD'
            )
            with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                length = resp.info().get('Content-Length')
                if length:
                    remote_bytes = int(length)
                    size_mb = remote_bytes / (1024 * 1024)
                    self.remote_file_size = size_mb

                    update_needed = False
                    if self.downloaded_file_path and os.path.exists(self.downloaded_file_path):
                        local_bytes = os.path.getsize(self.downloaded_file_path)
                        file_mtime = os.path.getmtime(self.downloaded_file_path)
                        age_hours = (time.time() - file_mtime) / 3600
                        if abs(local_bytes - remote_bytes) > 50 * 1024 or age_hours > 20:
                            update_needed = True

                    self.after(0, lambda: self._apply_update_check_results(size_mb, update_needed))
        except Exception:
            pass

    def _apply_update_check_results(self, size_mb, update_needed):
        if self.downloading:
            return

        if self.downloaded_file_path and os.path.exists(self.downloaded_file_path):
            if update_needed:
                self.is_update_available = True
                self.status_badge.configure(text=self.tr("status_update_available"), text_color="#10B981")
                self.info_label.configure(text=self.tr("info_new_base").format(size_mb), text_color="#10B981")
                self.download_button.configure(
                    text=self.tr("btn_update").format(self.selected_utility),
                    fg_color=self.UPDATE_COLOR,
                    hover_color=self.UPDATE_HOVER
                )
            else:
                self.is_update_available = False
                self.status_badge.configure(text=self.tr("status_actual"), text_color="#3B82F6")
                self.info_label.configure(text=self.tr("info_actual_base"), text_color="#3B82F6")
                self.download_button.configure(
                    text=self.tr("btn_redownload"),
                    fg_color=self.ACCENT_COLOR,
                    hover_color=self.ACCENT_HOVER
                )
        else:
            self.size_label.configure(text=self.tr("size_approx").format(size_mb))

    def on_utility_change(self, choice):
        if self.downloading:
            self.util_selector.set(self.selected_utility)
            return
        self.selected_utility = choice
        self.config.set("last_utility", choice)
        self.check_existing_file()
        self.check_remote_updates_async()

    def toggle_sound_mode(self):
        self.config.set("sound_enabled", self.sound_enabled_var.get())

    def play_sound(self, sound_type="success"):
        if not self.config.get("sound_enabled"):
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

    def toggle_path_mode(self):
        if self.use_script_dir_var.get():
            downloads_dir = os.path.join(get_base_dir(), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, downloads_dir)
            self.path_entry.configure(state="readonly")
            self.browse_button.configure(state="disabled")
            self.config.set("downloads_folder", "Downloads")
        else:
            self.browse_button.configure(state="normal")
        self.check_existing_file()
        self.check_remote_updates_async()

    def browse_folder(self):
        selected_directory = filedialog.askdirectory(
            title=self.tr("browse_dialog_title"),
            initialdir=self.path_entry.get()
        )
        if selected_directory:
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, selected_directory)
            self.path_entry.configure(state="readonly")
            self.config.set("downloads_folder", selected_directory)
            self.check_existing_file()
            self.check_remote_updates_async()

    def handle_download_click(self):
        if self.downloading:
            self.cancel_requested = True
            self.download_button.configure(text=self.tr("btn_canceling"), state="disabled")
        else:
            self.start_download_thread()

    def start_download_thread(self):
        self.downloading = True
        self.cancel_requested = False
        
        self.download_button.configure(
            text=self.tr("btn_cancel"),
            fg_color=self.CANCEL_COLOR,
            hover_color=self.CANCEL_HOVER,
            state="normal"
        )
        self.action_button.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.same_folder_checkbox.configure(state="disabled")
        self.util_selector.configure(state="disabled")

        self.status_badge.configure(text=self.tr("status_connecting"), text_color="#06B6D4")
        self.info_label.configure(text=self.tr("info_connecting"), text_color="#06B6D4")

        threading.Thread(target=self.download_process, daemon=True).start()

    def download_process(self):
        util_info = UTILITIES[self.selected_utility]
        url = util_info["download_url"]
        target_dir = self.path_entry.get()
        os.makedirs(target_dir, exist_ok=True)

        is_archive = util_info.get("is_archive", False)
        if is_archive:
            filename = util_info.get("archive_filename", "archive.zip")
            extract_dir = os.path.join(target_dir, self.selected_utility)
            os.makedirs(extract_dir, exist_ok=True)
            save_path = os.path.join(extract_dir, filename)
        else:
            filename = util_info.get("default_filename", "installer.exe")
            extract_dir = target_dir
            save_path = os.path.join(target_dir, filename)

        temp_save_path = save_path + ".tmp"

        ctx = ssl.create_default_context()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': util_info["referer"],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                if response.status != 200:
                    raise Exception(f"Server returned status {response.status}")

                cd_header = response.info().get('Content-Disposition')
                parsed_filename = parse_content_disposition(cd_header)
                if parsed_filename and not is_archive:
                    save_path = os.path.join(target_dir, parsed_filename)
                    temp_save_path = save_path + ".tmp"

                total_size = int(response.info().get('Content-Length', 0))
                downloaded = 0
                block_size = 1024 * 64
                start_time = time.time()
                sha256_hash = hashlib.sha256()

                with open(temp_save_path, 'wb') as out_file:
                    while True:
                        if self.cancel_requested:
                            raise Exception("Download canceled by user")

                        buffer = response.read(block_size)
                        if not buffer:
                            break

                        downloaded += len(buffer)
                        sha256_hash.update(buffer)
                        out_file.write(buffer)

                        dl_mb = downloaded / (1024 * 1024)
                        tot_mb = total_size / (1024 * 1024) if total_size > 0 else 0
                        progress = downloaded / total_size if total_size > 0 else 0

                        elapsed = time.time() - start_time
                        speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                        eta_sec = int((total_size - downloaded) / (speed * 1024 * 1024)) if speed > 0 and total_size > 0 else 0

                        self.after(0, self.update_download_status, dl_mb, tot_mb, progress, speed, eta_sec)

                if downloaded < 10 * 1024:
                    raise Exception("Downloaded file is too small")

                if not is_archive:
                    with open(temp_save_path, 'rb') as check_file:
                        header_bytes = check_file.read(2)
                        if header_bytes != b'MZ':
                            raise Exception("Downloaded file is not a valid Windows executable (.exe)")

            if os.path.exists(save_path):
                os.remove(save_path)
            os.rename(temp_save_path, save_path)

            final_hash = sha256_hash.hexdigest()
            print(f"[{self.selected_utility}] SHA-256: {final_hash}")

            if is_archive:
                with zipfile.ZipFile(save_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

                target_exe = None
                for file_name in os.listdir(extract_dir):
                    if file_name.lower().endswith(".exe"):
                        target_exe = os.path.join(extract_dir, file_name)
                        break

                if target_exe:
                    self.downloaded_file_path = target_exe
                else:
                    self.downloaded_file_path = save_path
            else:
                self.downloaded_file_path = save_path

            self.after(0, self.on_download_complete)

        except Exception as e:
            if os.path.exists(temp_save_path):
                try:
                    os.remove(temp_save_path)
                except Exception:
                    pass
            self.after(0, self.on_download_error, str(e))

    def update_download_status(self, dl_mb, tot_mb, progress, speed, eta_sec):
        self.progress_bar.set(progress)
        self.status_badge.configure(text=self.tr("status_downloading"), text_color="#06B6D4")
        
        if tot_mb > 0:
            self.size_label.configure(text=f"{dl_mb:.1f} МБ / {tot_mb:.1f} МБ")
            self.info_label.configure(text=self.tr("info_download_speed").format(speed, eta_sec), text_color="#06B6D4")
        else:
            self.size_label.configure(text=f"{dl_mb:.2f} МБ")
            self.info_label.configure(text=f"{speed:.2f} МБ/с", text_color="#06B6D4")

    def on_download_complete(self):
        self.downloading = False
        self.is_update_available = False
        self.play_sound("success")
        self.status_badge.configure(text=self.tr("status_actual"), text_color="#10B981")
        self.info_label.configure(text=self.tr("info_updated_signatures"), text_color="#10B981")
        
        self.download_button.configure(
            text=self.tr("btn_redownload"),
            fg_color=self.ACCENT_COLOR,
            hover_color=self.ACCENT_HOVER,
            state="normal"
        )
        self.action_button.configure(state="normal")
        self.same_folder_checkbox.configure(state="normal")
        self.util_selector.configure(state="normal")
        if not self.use_script_dir_var.get():
            self.browse_button.configure(state="normal")

    def on_download_error(self, err_msg):
        self.downloading = False
        self.download_button.configure(
            text=self.tr("btn_download").format(self.selected_utility),
            fg_color=self.ACCENT_COLOR,
            hover_color=self.ACCENT_HOVER,
            state="normal"
        )
        self.same_folder_checkbox.configure(state="normal")
        self.util_selector.configure(state="normal")
        if not self.use_script_dir_var.get():
            self.browse_button.configure(state="normal")

        if "canceled" in err_msg.lower() or "отменено" in err_msg.lower():
            self.play_sound("error")
            self.status_badge.configure(text=self.tr("status_canceled"), text_color="#9CA3AF")
            self.info_label.configure(text=self.tr("info_stopped"), text_color="#9CA3AF")
            self.progress_bar.set(0)
        else:
            self.play_sound("error")
            self.status_badge.configure(text=self.tr("status_error"), text_color="#EF4444")
            self.info_label.configure(text=self.tr("info_failed"), text_color="#EF4444")
            messagebox.showerror(self.tr("err_download_title"), self.tr("err_download_msg").format(err_msg))

    def run_downloaded_file(self):
        if self.downloaded_file_path and os.path.exists(self.downloaded_file_path):
            try:
                os.startfile(self.downloaded_file_path)
            except Exception as e:
                messagebox.showerror(self.tr("err_run_title"), self.tr("err_run_msg").format(e))

    def open_download_folder(self):
        target_dir = self.path_entry.get()
        if UTILITIES[self.selected_utility].get("is_archive", False):
            subfolder = os.path.join(target_dir, self.selected_utility)
            if os.path.exists(subfolder):
                target_dir = subfolder

        if os.path.exists(target_dir):
            if sys.platform == "win32":
                os.startfile(target_dir)
            else:
                subprocess.Popen(["xdg-open", target_dir])

    def on_closing(self):
        if self.downloading:
            self.cancel_requested = True
        self.destroy()

if __name__ == "__main__":
    app = CyberDownloaderApp()
    app.mainloop()