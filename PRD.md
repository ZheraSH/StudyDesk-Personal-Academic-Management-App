# Product Requirements Document

## 1. Product Overview

**Product Name:** StudyDesk
**Product Type:** Personal Academic Management Application
**Target Platform:** Windows Desktop + Android
**Technology:** Python, Flet, SQLite, SQLAlchemy
**Architecture:** Local-first, single-user, offline-first

StudyDesk adalah aplikasi pribadi untuk membantu mahasiswa mengelola aktivitas akademik dalam satu tempat.

Aplikasi berfokus pada empat hal utama:

1. Jadwal kuliah dan praktikum.
2. Manajemen tugas dan deadline.
3. Pengingat tugas dan agenda akademik.
4. Manajemen waktu pengerjaan tugas.

Aplikasi tidak membutuhkan login, akun pengguna, server, backend API, atau cloud untuk fitur utama.

Semua data disimpan secara lokal dalam SQLite.

---

# 2. Problem Statement

Mahasiswa sering menerima informasi akademik dari banyak sumber:

* WhatsApp
* Google Classroom
* LMS kampus
* Grup kelas
* File PPT/PDF
* Informasi langsung dari dosen
* Catatan pribadi

Masalahnya bukan selalu lupa bahwa tugas ada, tetapi lupa:

* tugasnya apa,
* mata kuliahnya apa,
* kapan deadline,
* kapan harus mulai mengerjakan,
* berapa lama waktu yang tersedia,
* dan tugas mana yang harus diprioritaskan.

StudyDesk dibuat untuk menjadi pusat kontrol pribadi terhadap semua aktivitas tersebut.

---

# 3. Goals

### Primary Goals

StudyDesk harus membantu pengguna:

* mengetahui jadwal hari ini,
* mengetahui tugas yang harus segera dikerjakan,
* mengetahui deadline terdekat,
* mencatat tugas dengan cepat,
* mendapatkan pengingat otomatis,
* memperkirakan waktu pengerjaan,
* melihat beban akademik dalam satu minggu.

### Secondary Goals

Aplikasi juga harus:

* bekerja tanpa internet,
* memiliki antarmuka nyaman untuk penggunaan sehari-hari,
* bisa digunakan di Windows,
* dapat dipasang sebagai APK Android,
* menjaga data pengguna tetap lokal.

---

# 4. Non-Goals

Versi awal tidak perlu:

* login,
* multi-user,
* chatting,
* sinkronisasi cloud,
* backend API,
* social features,
* integrasi LMS otomatis,
* AI assistant,
* sistem akademik kampus,
* collaborative task management.

Jangan memasukkan fitur hanya karena secara teknis bisa dibuat.

---

# 5. Target User

Primary user hanya satu:

**Mahasiswa pemilik aplikasi.**

Karakteristik:

* memiliki banyak mata kuliah,
* memiliki jadwal kuliah dan praktikum,
* menerima tugas secara rutin,
* membutuhkan deadline reminder,
* sering menggunakan smartphone,
* membutuhkan aplikasi yang cepat dan sederhana.

---

# 6. Core User Flow

## Flow A - Menambahkan Mata Kuliah

User membuka:

`Settings → Courses → Add Course`

Input:

* Course Name
* Course Code
* Lecturer
* Room
* Color/Icon
* Notes

Contoh:

```text
Course:
Pemrograman Web

Code:
TI204

Lecturer:
Pak Budi

Room:
Lab 2
```

---

## Flow B - Menambahkan Jadwal

User membuka:

`Schedule → Add Schedule`

Input:

* Course
* Schedule Type
* Day
* Start Time
* End Time
* Room
* Notes

Schedule Type:

```text
LECTURE
PRACTICUM
OTHER
```

Jadwal bersifat recurring.

Contoh:

```text
Pemrograman Web
Praktikum
Tuesday
13:00 - 15:00
Lab 2
```

---

# 7. Task Management

Task adalah fitur utama aplikasi.

User dapat membuat:

```text
Title
Course
Task Type
Description
Deadline
Priority
Estimated Duration
Status
Reminder
Attachment
Notes
```

### Task Type

```text
Assignment
Presentation
Report
Project
Quiz
Exam
Other
```

### Priority

```text
Low
Medium
High
Urgent
```

### Status

```text
Inbox
Planned
In Progress
Completed
Archived
```

---

# 8. Quick Add Task

User harus dapat membuat tugas dengan sangat cepat.

Contoh input:

```text
Buat PPT presentasi jaringan
Deadline Jumat 20 September 20:00
Mata kuliah Jaringan Komputer
```

Form tetap dapat dibuka untuk detail tambahan.

Target:

**Task baru dapat dibuat kurang dari 10 detik.**

---

# 9. Task Detail

Detail tugas menampilkan:

```text
Task Title

Course
Task Type
Priority
Status

Deadline
Time Remaining

Estimated Duration

Reminder

Description

Checklist

Attachment

Notes
```

Contoh:

```text
PPT Presentasi Jaringan

Jaringan Komputer
Presentation
HIGH

Deadline:
20 September 2026, 20:00

Remaining:
1 day 18 hours

Estimated:
120 minutes

Checklist:
[ ] Cari materi
[ ] Buat outline
[ ] Buat slide
[ ] Review
[ ] Submit
```

---

# 10. Dashboard

Dashboard adalah halaman utama.

Urutan informasi dari paling penting:

### Header

```text
Good Evening, Zhera

Friday, 18 September 2026
```

### Next Schedule

Menampilkan jadwal terdekat.

```text
NEXT CLASS

Pemrograman Web
13:00 - 15:00
Lab 2

Starts in 2h 20m
```

### Today's Schedule

Daftar kuliah/praktikum hari ini.

### Urgent Tasks

Tugas dengan deadline paling dekat.

### Upcoming Deadlines

Tugas:

```text
Today
Tomorrow
This Week
Next Week
```

### Academic Load

Contoh:

```text
5 Tasks Active
2 Deadlines This Week
1 Overdue
6 Classes
```

---

# 11. Calendar / Schedule

Schedule memiliki dua mode:

### Weekly View

```text
MON
TUE
WED
THU
FRI
SAT
```

Menampilkan seluruh kuliah dan praktikum.

### Agenda View

Contoh:

```text
TODAY

08:00
Database
Room 301

13:00
Web Programming
Lab 2

19:00
Finish Database Assignment
```

---

# 12. Reminder System

Reminder dapat dibuat pada setiap task.

Preset:

```text
3 Days Before
1 Day Before
12 Hours Before
3 Hours Before
1 Hour Before
30 Minutes Before
At Deadline
Custom
```

User dapat membuat beberapa reminder untuk satu task.

Contoh:

```text
Task:
Final Project Web

Reminder:
3 days before

Reminder:
1 day before

Reminder:
3 hours before
```

Notification:

```text
Assignment Reminder

Final Project Web

Deadline:
Tomorrow, 20:00

Estimated Duration:
3 hours
```

Pada Android, reminder harus menggunakan native/local notification layer dan tidak bergantung pada aplikasi yang sedang terbuka.

---

# 13. Overdue System

Jika deadline terlewati dan task belum selesai:

Status:

```text
OVERDUE
```

Dashboard harus menampilkan:

```text
3 OVERDUE TASKS
```

Tetapi jangan menghapus task otomatis.

User tetap dapat:

```text
Complete
Reschedule
Archive
```

---

# 14. Time Management

Setiap task mempunyai:

```text
Estimated Duration
```

Contoh:

```text
Assignment Database
Estimated: 120 minutes
```

Versi MVP menyediakan Focus Timer sederhana.

Mode:

```text
25 min focus
5 min break
```

User dapat mengganti:

```text
15 / 5
25 / 5
50 / 10
Custom
```

Timer tidak perlu terhubung ke backend.

---

# 15. Attachment

Task dapat mempunyai attachment.

Contoh:

```text
PPT Jaringan Komputer.pptx
Materi UTS.pdf
Instruksi Tugas.pdf
```

Metadata attachment:

```text
File Name
File Path / URI
File Type
Created At
```

File tidak perlu di-upload ke cloud.

Pada desktop, file dapat dibuka menggunakan aplikasi default OS.

Untuk Android, gunakan mekanisme file URI/platform-compatible storage dan jangan mengasumsikan path Windows dapat digunakan di Android.

---

# 16. Statistics

Dashboard statistik sederhana:

```text
Completed Tasks
Active Tasks
Overdue Tasks
Tasks Completed This Week
Estimated Workload
Actual Focus Time
```

Contoh:

```text
THIS WEEK

Completed:
8

Remaining:
5

Overdue:
1

Estimated Work:
7h 30m
```

---

# 17. Database Design

## semesters

```text
id
name
start_date
end_date
is_active
created_at
updated_at
```

## courses

```text
id
semester_id
name
code
lecturer
room
color
notes
created_at
updated_at
```

## schedules

```text
id
course_id
type
day_of_week
start_time
end_time
room
notes
is_active
created_at
updated_at
```

## tasks

```text
id
course_id
title
description
task_type
priority
status
deadline
estimated_minutes
planned_start
planned_end
completed_at
created_at
updated_at
```

## task_checklists

```text
id
task_id
title
is_completed
sort_order
created_at
updated_at
```

## reminders

```text
id
task_id
remind_at
reminder_type
is_enabled
is_sent
created_at
updated_at
```

## attachments

```text
id
task_id
file_name
file_path
file_type
file_size
created_at
```

## focus_sessions

```text
id
task_id
started_at
ended_at
duration_minutes
completed
created_at
```

## app_settings

```text
id
key
value
```

---

# 18. Architecture

Gunakan struktur modular sederhana:

```text
src/
├── main.py
├── config/
│   └── settings.py
│
├── database/
│   ├── connection.py
│   ├── models/
│   └── repositories/
│
├── services/
│   ├── task_service.py
│   ├── schedule_service.py
│   ├── reminder_service.py
│   ├── notification_service.py
│   └── focus_service.py
│
├── ui/
│   ├── pages/
│   ├── components/
│   ├── dialogs/
│   └── theme/
│
├── utils/
│   ├── datetime_utils.py
│   └── file_utils.py
│
└── assets/
```

Architecture principle:

```text
UI
 ↓
Service
 ↓
Repository
 ↓
SQLite
```

UI tidak boleh langsung melakukan query database.

Notification implementation harus melalui:

```text
ReminderService
      ↓
NotificationService
      ↓
Platform Adapter
      ↓
Native Notification
```

---

# 19. Offline First

Aplikasi harus tetap berfungsi tanpa internet.

Fitur utama yang wajib offline:

* schedule,
* task,
* deadline,
* reminder,
* focus timer,
* statistics,
* attachment metadata.

Internet tidak menjadi dependency untuk core functionality.

---

# 20. MVP Scope

### Phase 1

```text
Dashboard
Courses
Schedule
Task Management
Deadline
Priority
Task Status
SQLite
Basic Reminder
```

### Phase 2

```text
Android Notification
Attachment
Checklist
Focus Timer
Statistics
Weekly Calendar
```

### Phase 3

```text
Calendar Integration
Recurring Task
Backup/Restore
Import/Export
Theme customization
```

### Future

```text
Cloud Sync
AI Assistant
LMS Integration
Google Calendar
Google Drive
```

---

# 21. Success Metrics

Aplikasi dianggap berhasil apabila user dapat:

1. Membuka aplikasi dan mengetahui apa yang harus dilakukan hari ini dalam kurang dari 10 detik.
2. Menambahkan tugas baru kurang dari 10 detik.
3. Melihat deadline terdekat tanpa membuka banyak halaman.
4. Mendapatkan reminder sebelum deadline.
5. Melihat jadwal kuliah dan praktikum mingguan.
6. Menggunakan aplikasi tanpa internet.

---

# 22. Design Principle

StudyDesk harus terasa seperti:

**"Digital academic desk milik sendiri."**

Bukan:

* corporate dashboard,
* ERP kampus,
* SaaS startup,
* productivity app generik.

Visual menggunakan:

**Muted Royal Purple + Soft Skeuomorphism + Desktop Organizer aesthetic.**

Interface harus terasa seperti benda fisik digital:

* panel seperti kertas,
* tombol seperti tombol fisik,
* inset area seperti notebook,
* raised cards,
* subtle bevel,
* soft shadow,
* slight gradient,
* rounded corners.

Tetapi jangan membuatnya seperti Windows 98 yang baru ditemukan kembali oleh arkeolog UI.

---
