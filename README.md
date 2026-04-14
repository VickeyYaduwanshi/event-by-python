# 🎓 Campus Events Hub — Django Project

A complete college event management system with 3 user roles: Student, Organizer, and Admin.

## 🚀 Quick Setup

### 1. Install dependencies
```bash
cd college_events
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py makemigrations accounts organizer_app student_app admin_panel
python manage.py migrate
```

### 3. Create initial data (admin + sample users)
```bash
python manage.py setup_initial_data
```

### 4. Run server
```bash
python manage.py runserver
```

### 5. Open in browser
```
http://127.0.0.1:8000/
```

---

## 🔑 Login Credentials

| Role      | Username   | Password |
|-----------|-----------|----------|
| Admin     | user-219  | 8120     |
| Organizer | organizer1 | org123   |
| Student   | student1  | stu123   |

---

## 📁 Project Structure

```
college_events/
├── college_events/       # Main Django project (settings, urls, wsgi)
├── landing/              # Landing page app
├── accounts/             # Login, Register, UserProfile model
├── organizer_app/        # Event creation, announcements, attendance
├── student_app/          # Registration, tickets, certificates, feedback
├── admin_panel/          # Event approval, user management, analytics
├── templates/            # All HTML templates
│   ├── base.html
│   ├── landing/
│   ├── accounts/
│   ├── organizer/
│   ├── student/
│   ├── admin_panel/
│   └── includes/         # Sidebar partials
├── static/               # CSS, JS, images
├── media/                # Uploaded files (posters, profile pics)
├── db.sqlite3            # SQLite database (auto-created)
└── manage.py
```

---

## ✨ Features

### 🔑 Admin
- Approve / Reject / Request Correction on events
- Manage all users (activate/deactivate)
- View platform analytics
- Issue certificates to participants

### 🎯 Organizer
- Create events (go to admin for approval first)
- Edit events sent for correction
- Live attendance tracker with check-in
- Send announcements to registered students
- Issue participation/winner certificates
- View event analytics

### 🎓 Student
- Browse & search active events
- Register for events (solo or team)
- View QR entry ticket
- Get checked in at events
- Download certificates
- Rate & give feedback on attended events

---

## 🔄 Event Flow

```
Organizer creates event
        ↓
   Status: PENDING
        ↓
  Admin reviews
    ↙        ↘
ACTIVE     CORRECTION / REJECTED
  ↓
Students register
  ↓
Organizer checks in students
  ↓
Admin/Organizer issues certificates
  ↓
Status: COMPLETED
```

---

## 🛠️ Tech Stack
- **Backend**: Django 4.2
- **Database**: SQLite
- **Auth**: Django built-in auth + custom UserProfile
- **Frontend**: Pure HTML/CSS (no external frameworks — all inline styles)
- **File storage**: Local media/ directory
