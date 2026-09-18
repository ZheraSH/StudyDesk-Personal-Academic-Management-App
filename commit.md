# 📋 Panduan Commit Bertahap (Modular Commit Guide)
## StudyDesk — Personal Academic Management App

Dokumen ini memandu Anda melakukan commit kode ke GitHub secara terstruktur, rapi, dan terbagi ke dalam **9 sesi logis**. 

Dengan membagi commit per lapisan arsitektur/fitur, riwayat Git Anda akan sangat mudah dibaca, di-*review*, di-*revert* jika diperlukan, dan di-*maintain* di kemudian hari (dibandingkan melakukan 1 commit raksasa berisi ribuan file).

> [!NOTE]
> **Penting:** File `.gitignore` telah dikonfigurasi di root proyek untuk otomatis mengecualikan folder `build/`, `.venv/`, `__pycache__/`, dan file *temporary*. Dengan demikian, file yang Anda commit **hanya** kode sumber inti aplikasi (~70 file), bukan 6.000+ file *build/cache*.

---

### 🚀 Cara Penggunaan Singkat
Jalankan perintah Git pada setiap sesi secara berurutan di terminal (PowerShell / Command Prompt / Git Bash) pada direktori proyek:
`C:\laragon\www\Project_Pribadi\StudyDesk-Personal-Academic-Management-App`

---

## 📦 Sesi 1: Konfigurasi Proyek & Dokumentasi Dasar
**Tujuan:** Menyimpan konfigurasi dependensi, filter Git, metadata aplikasi, dan dokumentasi README utama.

```bash
git add .gitignore pyproject.toml requirements.txt README.md commit.md
git commit -m "chore(config): setup dependencies, gitignore, and project documentation"
```

**File yang Di-commit:**
- `.gitignore` (Mencegah file cache, .venv, dan build flutter ter-commit)
- `pyproject.toml` (Metadata proyek, konfigurasi build Flet, dan izin Android)
- `requirements.txt` (Daftar dependensi Python)
- `README.md` (Dokumentasi instruksi instalasi & fitur)
- `commit.md` (Panduan tahapan commit bertahap)

---

## 🗄️ Sesi 2: Engine Database & Model ORM (Entities)
**Tujuan:** Menyimpan konfigurasi dasar aplikasi, koneksi database SQLite, dan seluruh model entitas data (SQLAlchemy ORM).

```bash
git add src/config/ src/database/__init__.py src/database/connection.py src/database/models/
git commit -m "feat(db): implement SQLite engine, base declarative model, and entity schemas"
```

**File yang Di-commit:**
- `src/config/` (`settings.py`, `__init__.py`)
- `src/database/connection.py` (Koneksi SQLite thread-safe & session lifecycle)
- `src/database/models/` (`base.py`, `semester.py`, `course.py`, `task.py`, `task_checklist.py`, `schedule.py`, `reminder.py`, `attachment.py`, `focus_session.py`, `app_setting.py`)

---

## 📂 Sesi 3: Lapisan Repository Database (Data Access Layer)
**Tujuan:** Menyimpan abstraksi akses data terisolasi untuk setiap entitas database.

```bash
git add src/database/repositories/
git commit -m "feat(db): add repository layer for isolated data access and queries"
```

**File yang Di-commit:**
- `src/database/repositories/base_repository.py` (Base generic repository CRUD)
- `src/database/repositories/task_repository.py`
- `src/database/repositories/course_repository.py`
- `src/database/repositories/schedule_repository.py`
- `src/database/repositories/semester_repository.py`
- `src/database/repositories/reminder_repository.py`
- `src/database/repositories/task_checklist_repository.py`
- `src/database/repositories/focus_session_repository.py`
- `src/database/repositories/attachment_repository.py`
- `src/database/repositories/app_setting_repository.py`

---

## 🌐 Sesi 4: Utilitas, Sistem Bahasa (i18n), dan Notifikasi
**Tujuan:** Menyimpan fungsi bantuan tanggal (Asia/Jakarta), validasi input, penyimpanan file, sistem bilingual ID/EN, dan adapter notifikasi lintas platform.

```bash
git add src/utils/ src/notifications/
git commit -m "feat(core): add datetime utilities, bilingual i18n support, and notification adapters"
```

**File yang Di-commit:**
- `src/utils/datetime_utils.py` (Perhitungan deadline relatif, timezone aware, format tanggal lokal)
- `src/utils/i18n.py` (Dukungan penuh Bahasa Indonesia & English dengan 300+ translation keys)
- `src/utils/validation.py` & `file_utils.py`
- `src/notifications/` (`base_adapter.py`, `adapter_factory.py`, `windows_adapter.py`, `android_adapter.py`)

---

## ⚙️ Sesi 5: Logika Bisnis (Business Logic Services)
**Tujuan:** Menyimpan lapisan service yang mengelola aturan bisnis, validasi alur kerja, fokus Pomodoro, dan kalkulasi statistik.

```bash
git add src/services/
git commit -m "feat(services): implement core academic business logic, scheduling, focus timer, and backup"
```

**File yang Di-commit:**
- `src/services/task_service.py` (Alur kerja tugas, urgensi, status)
- `src/services/schedule_service.py` (Deteksi konflik jadwal kuliah mingguan)
- `src/services/focus_service.py` (Pencatatan sesi Pomodoro & statistik durasi)
- `src/services/statistics_service.py` (Agregasi metrik produktivitas & beban tugas)
- `src/services/backup_service.py` (Export/Import CSV, JSON, dan SQLite zip)
- `src/services/course_service.py`, `checklist_service.py`, `reminder_service.py`, `notification_service.py`, `settings_service.py`, `attachment_service.py`

---

## 🎨 Sesi 6: Sistem Desain UI & Komponen Bersama (Shared Components)
**Tujuan:** Menyimpan tema warna, tipografi, sidebar desktop, bottom navigation mobile, dan kartu UI interaktif.

```bash
git add src/ui/__init__.py src/ui/theme/ src/ui/components/
git commit -m "feat(ui): implement design system tokens, layout navigation, and shared components"
```

**File yang Di-commit:**
- `src/ui/theme/theme.py` (Token warna elegan, radius, tipografi)
- `src/ui/components/sidebar.py` (Navigasi desktop)
- `src/ui/components/bottom_nav.py` (Navigasi responsif untuk mobile)
- `src/ui/components/shared.py` (Button, Card, Badge, Banner, Dropdown kustom)
- `src/ui/components/task_card.py`, `schedule_card.py`, `checklist_item.py`, `attachment_row.py`

---

## 💬 Sesi 7: Dialog Interaktif (Modal Dialogs)
**Tujuan:** Menyimpan formulir modal untuk penambahan cepat tugas, pengeditan tugas lengkap, jadwal, dan mata kuliah.

```bash
git add src/ui/dialogs/
git commit -m "feat(ui): implement modal dialogs for quick add, task, schedule, and course management"
```

**File yang Di-commit:**
- `src/ui/dialogs/quick_add_dialog.py` (Dialog input tugas cepat <10 detik)
- `src/ui/dialogs/task_dialog.py` (Formulir detail tugas akademik)
- `src/ui/dialogs/schedule_dialog.py` (Formulir jadwal kuliah)
- `src/ui/dialogs/course_dialog.py` (Formulir mata kuliah & skema warna)

---

## 📱 Sesi 8: Halaman Utama Aplikasi & Entry Point Controller
**Tujuan:** Menyimpan 7 halaman utama aplikasi dan controller utama yang menghubungkan UI desktop/mobile.

```bash
git add src/ui/pages/ src/__init__.py src/main.py main.py
git commit -m "feat(ui): build full application views and main controller with mobile/desktop support"
```

**File yang Di-commit:**
- `src/ui/pages/dashboard_page.py` (Halaman Beranda)
- `src/ui/pages/schedule_page.py` (Halaman Jadwal Mingguan & Agenda)
- `src/ui/pages/tasks_page.py` & `task_detail_page.py` (Manajemen Tugas)
- `src/ui/pages/focus_page.py` (Halaman Timer Pomodoro)
- `src/ui/pages/statistics_page.py` (Halaman Statistik Akademik)
- `src/ui/pages/settings_page.py` (Halaman Pengaturan & Backup)
- `src/main.py` & `main.py` (Controller utama & bootstrap aplikasi)

---

## 🧪 Sesi 9: Pengujian Otomatis (Automated Test Suite)
**Tujuan:** Menyimpan rangkaian 31 unit test dan pengujian integrasi end-to-end.

```bash
git add tests/
git commit -m "test: add comprehensive test suite with 31 unit and e2e integration tests"
```

**File yang Di-commit:**
- `tests/conftest.py` (Fixture SQLite in-memory untuk pengujian cepat & terisolasi)
- `tests/test_task_service.py`
- `tests/test_schedule_service.py`
- `tests/test_focus_service.py`
- `tests/test_reminder_service.py`
- `tests/test_statistics_service.py`
- `tests/test_course_service.py`
- `tests/test_checklist_service.py`
- `tests/test_backup_service.py`
- `tests/test_datetime_utils.py`
- `tests/test_e2e_features.py` (Pengujian alur lengkap mahasiswa)

---

## 📤 Langkah Terakhir: Push ke GitHub

Setelah semua 9 sesi selesai di-commit secara lokal, kirimkan seluruh commit tersebut ke repositori GitHub:

```bash
# Periksa status (pastikan working tree clean)
git status

# Periksa riwayat 9 commit Anda
git log --oneline -n 10

# Push ke remote repository
git push origin main
```

---

### 💡 Tips Berguna:
- **Jika ingin membatalkan staging sebelum commit:**
  ```bash
  git restore --staged <file-atau-folder>
  ```
- **Jika ingin mengecek commit terakhir:**
  ```bash
  git log -1 --stat
  ```
