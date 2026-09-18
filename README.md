# 📚 StudyDesk — Personal Academic Management App

A production-quality, offline-first academic management application built for a single university student. Manage your courses, schedules, assignments, deadlines, study sessions, and progress — all in one clean, fast, local desktop app.

---

## ✨ Features

| Module | What it does |
|---|---|
| **Dashboard** | Morning greeting, next upcoming class, overdue warnings, urgent tasks, quick stats |
| **Schedule** | Weekly timetable, lecture/practicum/other types, conflict detection |
| **Tasks** | Full task lifecycle (Inbox → Planned → In Progress → Completed), filtering, sorting, checklist sub-items |
| **Task Detail** | Rich task view with checklist, attachments, reminders, and one-click "Start Focus" |
| **Focus Timer** | Pomodoro-style timer (15/5, 25/5, 50/10 presets), session recording, linked task |
| **Statistics** | Completion rates, weekly focus time, workload estimate, overdue health check |
| **Settings** | Profile, active semester, notification preferences, backup & restore, data export (CSV / JSON) |
| **Reminders** | Up to 5 reminders per task, preset offsets (3 days → at deadline), Windows toast support |
| **Attachments** | Link files to tasks, stored in app data dir |

---

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **UI:** [Flet](https://flet.dev/) (cross-platform Flutter-based GUI)
- **Database:** SQLite via SQLAlchemy 2.x (async-safe, single-user)
- **Design System:** Muted Royal Purple Skeuomorphism (custom tokens in `src/config/settings.py`)
- **Platform targets:** Windows desktop, Android (same codebase)
- **No external APIs, no internet required.**

---

## 📁 Project Structure

```
src/
├── config/
│   └── settings.py           # All design tokens, paths, and constants
├── database/
│   ├── connection.py          # SQLAlchemy engine + context manager
│   ├── models/                # 10 SQLAlchemy models
│   └── repositories/          # Repository layer (11 repos, BaseRepository CRUD)
├── services/                  # Business logic (12 services)
│   ├── task_service.py
│   ├── schedule_service.py
│   ├── reminder_service.py
│   ├── focus_service.py
│   ├── statistics_service.py
│   ├── backup_service.py
│   └── ...
├── ui/
│   ├── theme/theme.py         # Flet theme configuration
│   ├── components/            # Reusable widgets (shared.py, sidebar, cards, etc.)
│   ├── pages/                 # 7 full pages
│   └── dialogs/               # Add/edit dialogs for tasks, courses, schedules
├── notifications/             # Platform-specific notification adapters
├── utils/                     # datetime_utils, file_utils, validation
└── main.py                    # App entry point + routing
tests/                         # 30 pytest tests (all passing)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or newer
- Windows 10+ (for desktop) or an Android device (via Flet packaging)

### Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd StudyDesk-Personal-Academic-Management-App

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
python src/main.py
```

The app will:
1. Create the SQLite database at `%APPDATA%\StudyDesk\studydesk.db`
2. Seed a default semester if none exists
3. Open the desktop window (1200 × 800, resizable)

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

All 30 tests run with an in-memory SQLite database and no external dependencies.

---

## 📦 Data Storage

All data is stored locally in:

| Path | Content |
|---|---|
| `%APPDATA%\StudyDesk\studydesk.db` | SQLite database |
| `%APPDATA%\StudyDesk\attachments\` | Task attachments |
| `%APPDATA%\StudyDesk\backups\` | Database backups + CSV/JSON exports |
| `%APPDATA%\StudyDesk\logs\` | Application log file |

### Backup & Export

From the **Settings** page you can:
- **Backup database** — copies the `.db` file with timestamp
- **Export CSV** — all tasks as a spreadsheet
- **Export JSON** — full data export (tasks, courses, schedules, semesters)
- **Restore** — import a previously backed-up `.db` file

---

## 🎨 Design System

The app uses a **Muted Royal Purple Skeuomorphism** design language:

- **Primary:** `#6F5A8E` (muted royal purple)
- **Background:** `#F4F1F7` (warm lavender white)
- **Surfaces:** multi-layered cards with subtle shadows and borders
- **Typography:** Segoe UI, carefully sized across 7 scale levels
- **Semantic colors:** all named after meaning (DANGER, SUCCESS, WARNING, INFO) rather than hue

All design tokens are in [`src/config/settings.py`](src/config/settings.py) — change them once, apply everywhere.

---

## 📱 Android Packaging

The same source code can be packaged for Android using Flet's build command:

```bash
flet build apk
```

The app detects `sys.platform == "android"` and:
- Switches to bottom navigation bar instead of sidebar
- Uses Flet's internal storage path for the database
- Adapts layouts for smaller screens

---

## 🗓️ Database Models

| Model | Key fields |
|---|---|
| `Semester` | name, academic_year, start/end date, is_active |
| `Course` | name, code, lecturer, room, color, semester_id |
| `Schedule` | course_id, day_of_week, start/end time, type (Lecture/Practicum/Other) |
| `Task` | title, type, priority, status, deadline, estimated_minutes, description |
| `TaskChecklist` | task_id, text, is_done, sort_order |
| `Reminder` | task_id, remind_at, offset_preset, is_sent |
| `Attachment` | task_id, filename, file_path, file_size |
| `FocusSession` | task_id, started_at, ended_at, duration_minutes, completed |
| `AppSetting` | key, value (key-value store for profile, preferences) |

---

## 📝 License

Personal use. Not licensed for redistribution.
