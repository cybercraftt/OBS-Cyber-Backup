# 📦 OBS Cyber Backup Utility



**OBS Cyber Backup Utility** is a compact Windows tool for backing up and restoring **OBS Studio** settings, scenes, profiles, and installed plugins[cite: 4].

The program is designed for situations where you need to save a working OBS configuration before reinstalling Windows, moving OBS to another computer, or making system changes[cite: 4].

> ⚠️ OBS Studio must be closed before backing up or restoring[cite: 4].

## ✨ Features

* 📦 Create OBS Studio backup in a ZIP archive[cite: 4]
* 🔄 Restore settings from a ZIP backup[cite: 4]
* 🎬 Backup OBS scenes, profiles, and settings[cite: 4]
* 🔌 Save OBS plugins[cite: 4]
* ☑️ Select components for backup[cite: 4]
* 🛡️ Verify created ZIP archive after operation completion[cite: 4]
* 📋 `backup_info.json` containing information about the created backup[cite: 4]
* 🔍 Verify selected archive before restoring[cite: 4]
* 🚫 Check if OBS Studio is running prior to operation[cite: 4]
* 📊 Display operation progress[cite: 4]
* 🔊 Audio notification upon successful completion[cite: 4]
* 📝 Automatic logging[cite: 4]
* 🌐 Dual language interface (Russian and English)[cite: 4]
* 💾 Save application settings[cite: 4]
* 🖥️ Support for running as a Python script and as a standalone Windows build[cite: 4]

## 🗂️ What Can Be Saved

The program allows you to selectively choose the following components[cite: 4]:

### AppData

OBS Studio settings, scenes, and user profiles[cite: 4].

```text
%APPDATA%\obs-studio
```[cite: 4]

### ProgramData

OBS Studio plugins[cite: 4]:

```text
%PROGRAMDATA%\obs-studio\plugins
```[cite: 4]

### Program Files

System-installed OBS Studio plugins[cite: 4]:

```text
C:\Program Files\obs-studio\obs-plugins
```[cite: 4]

This allows you to either perform a full OBS backup or save only the necessary components[cite: 4].

## 📦 Backup Format

Backups are created in the following format[cite: 4]:

```text
ZIP
```[cite: 4]

An additional file is placed inside the archive[cite: 4]:

```text
backup_info.json
```[cite: 4]

It stores information about the utility version, backup creation time, total file count, and selected components[cite: 4].

Example[cite: 4]:

```json
{
    "app": "OBS Cyber Backup Utility",
    "version": "1.1.0",
    "created": "2026-09-29 14:00:00",
    "total_files": 123,
    "appdata_obs": true,
    "programdata_plugins": true,
    "programfiles_plugins": true
}
```[cite: 4]

## 🔐 Backup Verification

After creating the ZIP archive, the program verifies its contents[cite: 4].

If the archive is corrupted, the operation is considered failed[cite: 4].

When restoring, the selected file is also verified before starting the operation[cite: 4].

## 🚨 Restoration Safety

Before restoring, the program checks[cite: 4]:

* whether OBS Studio is running;[cite: 4]
* if the selected file is a valid ZIP archive;[cite: 4]
* presence of backup metadata;[cite: 4]
* integrity of archive contents;[cite: 4]
* write permissions for required system directories.[cite: 4]

If OBS Studio is running, the program will ask you to close it first[cite: 4].

Modifying files in system directories may require running the application **as Administrator**[cite: 4].

## 💻 Transferring OBS to Another PC

The program includes a dedicated **"Transfer OBS to another PC"** feature that guides you through using the created backup to transfer your setup[cite: 4].

General Concept[cite: 4]:

```text
Old PC
   │
   ├── OBS Studio
   ├── Scenes
   ├── Profiles
   └── Plugins
          │
          ▼
     ZIP Backup
          │
          ▼
      New PC
          │
          └── Restore
```[cite: 4]

## 📝 Logs

When running, the program creates a directory[cite: 4]:

```text
logs
```[cite: 4]

It stores daily log files[cite: 4]:

```text
app_YYYY-MM-DD.log
```[cite: 4]

Logs help identify the root cause of errors if backing up or restoring fails[cite: 4].

## 🔊 Completion Notification

After a backup is successfully created, the program plays an audio notification[cite: 4].

This is particularly convenient when dealing with a large number of scenes, profiles, and plugins, where archive creation might take longer[cite: 4].

## 🖥️ Interface

The program features a modern dark interface built with **CustomTkinter**[cite: 4].

Key UI elements[cite: 4]:

* language selection;[cite: 4]
* component selection;[cite: 4]
* backup directory selection;[cite: 4]
* progress indicator;[cite: 4]
* backup creation;[cite: 4]
* restoration;[cite: 4]
* open backup folder;[cite: 4]
* transfer OBS to another PC.[cite: 4]

---

## 🖼️ Screenshot

![OBS Cyber Backup](https://raw.githubusercontent.com/cybercraftt/Smart-Shutdown/e0b20300db21105a2e92c8b7a73e326cdf52fa94/assets/screenshot.png)[cite: 4]

---

## ⚙️ Requirements

To run from source code[cite: 4]:

* Windows 10/11[cite: 4]
* Python 3.x[cite: 4]
* CustomTkinter[cite: 4]

Install dependency[cite: 4]:

```bash
pip install customtkinter
```[cite: 4]

## ▶️ Running from Source

Clone the repository[cite: 4]:

```bash
git clone https://github.com/cybercraftt/OBS-Cyber-Backup.git
cd OBS-Cyber-Backup
```[cite: 4]

Run the program[cite: 4]:

```bash
python "obs_cyber_backup.py"
```[cite: 4]

If your Python file uses a different name, use the corresponding filename from your repository[cite: 4].

## 📁 Project Structure

Sample structure[cite: 4]:

```text
OBS-Cyber-Backup/
│
├── obs_cyber_backup.py
├── alert.wav
├── README.md
├── LICENSE
│
├── Backups/
│
└── logs/
```[cite: 4]

The `Backups` and `logs` directories are generated automatically by the program as needed[cite: 4].

## 🛠️ Version

Current Version[cite: 4]:

**v1.1.0**[cite: 4]

Key changes in version 1.1.0[cite: 4]:

* added OBS running check;[cite: 4]
* added backup metadata information;[cite: 4]
* added ZIP verification post-creation;[cite: 4]
* added archive verification pre-restoration;[cite: 4]
* added selective component backup;[cite: 4]
* added logging functionality;[cite: 4]
* added detailed error modal window;[cite: 4]
* added audio notification;[cite: 4]
* added guided PC transfer wizard.[cite: 4]

## ⚠️ Important

This program interacts directly with OBS Studio directories[cite: 4].

It is recommended to maintain an independent copy of your current OBS settings before performing a restore[cite: 4].

Pay special attention when restoring plugins, as different versions of OBS Studio and third-party plugins may be incompatible with each other[cite: 4].

This program is not a replacement for standard Windows backup solutions and is specifically designed for convenient saving of OBS Studio configurations[cite: 4].

## ❤️ Support the Project

If this project helped you and you would like to support future development[cite: 4]:

* YouTube: **Cyber Craft**[cite: 4]
* Telegram: **CyberCraftLab**[cite: 4]
* Boosty: **Cyber Craft**[cite: 4]

---

## 📜 License

This project is distributed under the terms of the license specified in the [`LICENSE`](LICENSE) file[cite: 4].

If the repository uses the MIT License, include a `LICENSE` file containing the license text[cite: 4].