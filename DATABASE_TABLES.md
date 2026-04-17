# Database Tables - Relationships & Deep Dive

---

## 📊 TABLE STRUCTURE & RELATIONSHIPS

### **1. USER TABLE** 👤

**Purpose**: Django ka built-in user authentication table

```sql
Fields:
- id (PRIMARY KEY) - Auto increment
- username (UNIQUE) - Login ID
- email (UNIQUE) - Email address
- password (HASHED) - Encrypted password
- is_active - Account active/inactive status
- is_staff - Django admin access
- date_joined - Account creation date
- last_login - Last login timestamp
```

**Relationship with Others**:
- **1-to-1 with UserProfile**: Har user ka ek profile hota hai
- **1-to-Many with EventRegistration**: Ek user multiple events mein register kar sakta hai
- **1-to-Many with Certificate**: Ek user multiple certificates earn kar sakta hai
- **1-to-Many with Announcement**: Organizers/Admins announcements create kar sakte hain

---

### **2. USERPROFILE TABLE** 📋

**Purpose**: User ke college-specific aur role-based information store karta hai

```sql
Fields:
- id (PRIMARY KEY)
- user (FOREIGN KEY → User) - Link to Django User
- role (CharField) - Values: 'student', 'organizer', 'admin'
- enrollment_number (CharField, nullable) - Sirf students ke liye
- branch (CharField, nullable) - Sirf students ke liye
- profile_picture (ImageField) - Optional profile image
- bio (TextField) - Optional bio
- created_at (DateTimeField) - Profile creation date
- updated_at (DateTimeField) - Last profile update
```

**Relationship with Others**:
- **1-to-1 with User**: Har UserProfile ke liye exactly ek User hota hai
- **Linked indirectly to Event**: Organizer role wale users hi events create kar sakte hain
  
  **📍 Code Details (कहाँ है implementation):**
  
  **File**: `organizer_app/views.py`
  
  **Line 11-20** - Decorator check करता है:
  ```python
  def organizer_required(view_func):
      def wrapper(request, *args, **kwargs):
          if not request.user.is_authenticated:
              return redirect('/accounts/login/?role=organizer')
          try:
              if request.user.profile.role != 'organizer':  # ← Role check (Line 16)
                  messages.error(request, 'Access denied.')
                  return redirect('/')
          except UserProfile.DoesNotExist:
              return redirect('/')
          return view_func(request, *args, **kwargs)
      return wrapper
  ```
  
  **Line 45** - Event create करते समय:
  ```python
  @organizer_required  # ← First ye decorator ensure karta hai organizer hai
  def create_event(request):
      if request.method == 'POST':
          event = Event(
              organizer=request.user,  # ← Line 45: Automatically current user set hota hai
              title=request.POST.get('title'),
              ...
          )
  ```
  
  **Line 30** - Dashboard mein sirf apne events dikhte hain:
  ```python
  events = Event.objects.filter(organizer=request.user)  # ← Only logged-in organizer ke events
  ```
  
  **कैसे काम करता है:**
  1. Student या admin login करे to `organizer_required` decorator error देता है
  2. Organizer login करे to role check pass हो जाता है
  3. Event create करते time automatically `organizer=request.user` set होता है
  4. Database में Event table की `organizer` field स मैच करता है
  5. Dashboard मein `Event.objects.filter(organizer=request.user)` से sirf apne events filter होते हain
  
  **Security Flow**: UserProfile.role = 'organizer' → @organizer_required decorator → View execute → Event.organizer = current_user

- **Linked indirectly to Announcement**: Admin role wale users hi announcements create kar sakte hain
  
  **📍 Code Details (कहाँ है implementation):**
  
  **File**: `organizer_app/views.py` (line ~150-160, के around)
  
  **Admin check करने के लिए decorator:**
  ```python
  def admin_required(view_func):
      def wrapper(request, *args, **kwargs):
          if not request.user.is_authenticated:
              return redirect('/accounts/login/')
          try:
              if request.user.profile.role != 'admin':  # ← Admin role check
                  messages.error(request, 'Admin access only.')
                  return redirect('/')
          except UserProfile.DoesNotExist:
              return redirect('/')
          return view_func(request, *args, **kwargs)
      return wrapper
  ```
  
  **Announcement create करते समय:**
  ```python
  @admin_required
  def create_announcement(request):
      if request.method == 'POST':
          announcement = Announcement(
              created_by=request.user,  # ← Admin user automatically set
              subject=request.POST.get('subject'),
              ...
          )
          announcement.save()
  ```
  
  **कैसे काम करता है:**
  1. Role check पहले होता है (`request.user.profile.role != 'admin'`)
  2. अगर admin नहीं है to error redirect होता है
  3. Admin है to announcement creation allowed है
  4. `created_by` field automatically current user (admin) से fill होता है
  5. Database में announcement student/organizer से different set में store होता है

**Deep Dive**:
UserProfile table Django ke User model ko extend karta hai aur college-specific data add karta hai। Role define karta hai ki user ka kya access level hai। Students ke liye enrollment_number aur branch mandatory hote hain identification ke liye। Admin aur Organizer ke liye ye fields optional hote hain। Profile picture se dashboard personalization hoti hai।

---

### **3. EVENT TABLE** 🎪

**Purpose**: College events ki complete information store karta hai

```sql
Fields:
- id (PRIMARY KEY)
- organizer (FOREIGN KEY → User) - Event creator
- title (CharField) - Event name
- description (TextField) - Complete details
- event_date (DateField) - Event ka date
- event_time (TimeField) - Event start time
- end_time (TimeField) - Event end time
- venue (CharField) - Location
- category (CharField) - Type: sports, cultural, technical, academic, other
- max_capacity (IntegerField) - Maximum participants allowed
- registration_fee (DecimalField) - Entry cost (optional)
- poster (ImageField) - Event promotional image
- is_team_event (BooleanField) - Team-based or individual
- team_size (IntegerField) - Agar team event ho to min/max size
- status (CharField) - pending/approved/rejected/completed/cancelled
- created_at (DateTimeField) - Creation date
- updated_at (DateTimeField) - Last update
- admin_approval_required (BooleanField) - Event ko approve karne ke liye
```

**Relationship with Others**:
- **Many-to-1 with User (Organizer)**: Multiple events ek organizer create kar sakta hai
- **1-to-Many with EventRegistration**: Ek event par multiple students register kar sakte hain
- **1-to-Many with Certificate**: Ek event se multiple certificates issue hote hain
- **1-to-Many with Announcement**: Event-specific announcements ban sakti hain
- **Unique Constraint**: Event + date combination unique hona chahiye same venue par

**Deep Dive**:
Event table project ka core hai। Har event mein organizer, timing, capacity, aur approval status hote hain। Status field track karta hai event lifecycle (pending approval se completed tak)। max_capacity se crowd management hoti hai। is_team_event flag se registration flow change hota hai। Admin approval system ensure karta hai ke sirf legitimate events register hon।

---

### **4. EVENTREGISTRATION TABLE** 📝

**Purpose**: Student aur event ke beech ka relationship track karta hai

```sql
Fields:
- id (PRIMARY KEY)
- student (FOREIGN KEY → User) - Registering student
- event (FOREIGN KEY → Event) - Which event
- registration_date (DateTimeField) - Registration timestamp
- team_name (CharField, nullable) - Agar team event ho
- team_members (TextField, nullable) - Team members list (JSON/CSV)
- status (CharField) - registered/cancelled/attended/no_show
- check_in_time (DateTimeField, nullable) - When student checked in
- feedback_rating (IntegerField, nullable) - 1-5 rating after event
- feedback_text (TextField, nullable) - Comments after event
- created_at (DateTimeField)
- updated_at (DateTimeField)

Indexes:
- UNIQUE (student, event) - Duplicate registration prevent
```

**Relationship with Others**:
- **Many-to-1 with User**: Multiple registrations per student
- **Many-to-1 with Event**: Multiple students per event
- **linked to Certificate**: Ek registration se ek certificate generate hoti hai

**Deep Dive**:
EventRegistration junction table (bridge table) hai jo many-to-many relationship define karta hai। UNIQUE constraint ensure karta hai ki ek student ek event mein sirf ek baar register kar sakta hai। status field follow karta hai registration lifecycle (registered → attended/no_show → certificate generation)। check_in_time se event attendance track hoti hai। feedback system user experience collect karta hai। team_members field team-based events ke liye members store karta hai।

---

### **5. CERTIFICATE TABLE** 🏆

**Purpose**: Student ne event mein participate kiya iska proof store karta hai

```sql
Fields:
- id (PRIMARY KEY)
- student (FOREIGN KEY → User) - Who earned it
- event (FOREIGN KEY → Event) - For which event
- cert_type (CharField) - winner_1/winner_2/winner_3/participant/completed
- issued_date (DateField) - Certificate generation date
- certificate_number (CharField, UNIQUE) - Unique certificate ID
- skills_gained (TextField) - What student learned
- issued_at (DateTimeField) - Issue timestamp
- is_digital (BooleanField) - Digital format available
- is_physical (BooleanField) - Physical copy requested
- created_at (DateTimeField)

Indexes:
- student + event (for quick lookup)
```

**Relationship with Others**:
- **Many-to-1 with User**: Student multiple certificates earn kar sakta hai
- **Many-to-1 with Event**: Event se multiple certificates issue hote hain
- **linked to EventRegistration**: Sirf registered students ko hi certificate milta hai

**Deep Dive**:
Certificate table event ke baad automatic generate hota hai। Organizer ya admin cert_type decide karte hain (winner positions ya participation)। certificate_number unique identifier deta hai digital verification ke liye। skills_gained se student learning track hoti hai। Digital aur physical dono formats support hote hain। Certificate issue date event completion date ke same ya baad mein hota hai।

---

### **6. ANNOUNCEMENT TABLE** 📢

**Purpose**: Organizers aur admins by students ko communicate karte hain

```sql
Fields:
- id (PRIMARY KEY)
- created_by (FOREIGN KEY → User) - Organizer/Admin who created
- event (FOREIGN KEY → Event, nullable) - Event-specific ya general
- subject (CharField) - Announcement title
- message (TextField) - Full message content
- priority (CharField) - low/medium/high/urgent
- target_audience (CharField) - all/students/organizers/admin
- is_published (BooleanField) - Draft ya published
- published_date (DateTimeField, nullable) - When it went live
- expiry_date (DateTimeField, nullable) - When it expires
- attachment (FileField, nullable) - PDF/document
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

**Relationship with Others**:
- **Many-to-1 with User (creator)**: Ek organizer multiple announcements create kar sakta hai
- **Many-to-1 with Event (optional)**: Event-specific announcements ho sakte hain
- **Linked to many Users (viewers)**: Through role-based visibility

**Deep Dive**:
Announcement table one-way communication channel hai। Creator organizer ya admin ho sakte hain। Event field null hota hai agar announcement general ho। Priority field decide karta hai announcement ki urgency (dashboard par color-coding)। target_audience se visibility control hota hai (sirf relevant users ko dikhta hai)। expiry_date se stale announcements auto-hide ho ja sakte hain। Publication status drafts save karne ka option deta hai।

---

## � ROLE-BASED ACCESS CONTROL DETAILED FLOW

### **Event Creation Access Control**

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: User Navigates to /organizer/create_event/      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Decorator ejecute होता है  │
        │ @organizer_required        │
        └────┬───────────────────────┘
             │
             ├─ authenticated? → NO → redirect /accounts/login/?role=organizer
             │
             └─ CHECK: request.user.profile.role == 'organizer'?
                       │
                       ├─ NO → Error message + redirect home
                       │
                       └─ YES ↓
                         ┌──────────────────────────┐
                         │ create_event() view runs │
                         └────┬─────────────────────┘
                              │
                              ▼
                    Event form submit होता है
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │ Event object create होता है:            │
        │ event = Event(                          │
        │     organizer=request.user,  ← SET    │
        │     title="Hackathon",                  │
        │     status='pending'                    │
        │ )                                       │
        └────┬────────────────────────────────────┘
             │
             ▼
     ┌──────────────────────┐
     │ Database save होता है│
     │ EventTable.organizer │
     │ = Vicky (User.id=1)  │
     └──────────────────────┘
```

**Code Example से समझो:**

```python
# organizer_app/views.py - Line 11-20

@organizer_required  # ← STEP 1: Role check
def create_event(request):
    if request.method == 'POST':
        # STEP 2: Event create करते time automatically organizer set
        event = Event(
            organizer=request.user,  # ← Line 45: request.user (current logged-in organizer)
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            category=request.POST.get('category'),
            # ... other fields
            status='pending',  # Approval के लिए pending
        )
        # STEP 3: Database में save होता है
        event.save()
        messages.success(request, 'Event submitted for admin approval!')
        return redirect('organizer_dashboard')
```

### **Dashboard Mein Sirf Apne Events:**

```python
# organizer_app/views.py - Line 30

@organizer_required
def dashboard(request):
    # STEP 1: Filter करो सिर्फ वही events जिनका organizer = current user
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    
    # STEP 2: यह query generate करता है:
    # SELECT * FROM event WHERE organizer_id = 1  (assuming request.user.id = 1)
    
    # STEP 3: Results mein सिर्फ वही events आते हैं:
    # - Event.id=5, organizer_id=1, title="Hackathon" ✓
    # - Event.id=6, organizer_id=1, title="Coding Contest" ✓
    # - Event.id=7, organizer_id=2, title="Sports Day" ✗ (different organizer)
```

---

### **Database Level - Foreign Key Constraint**

```sql
-- organizer_app/models.py में Event model

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)  # ← Line में ForeignKey
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('active', 'Active'),
            ('completed', 'Completed'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # UNIQUE constraint: एक organizer एक ही event create कर सकता है
        unique_together = [['organizer', 'title', 'event_date']]
        # ↑ Same title, same date par duplicate prevent करता है
```

**Actual SQL Query में:**

```sql
-- जब Vicky (User.id=1) event create करे:
INSERT INTO event_table (organizer_id, title, reference_date, status) 
VALUES (1, 'Hackathon 2025', '2026-04-20', 'pending');

-- Foreign Key Constraint check होता है:
-- Does organizer_id=1 exist in User table? YES ✓
-- Unique constraint check: 
-- Is there another event with (organizer_id=1, title='Hackathon 2025', event_date=2026-04-20)? NO ✓
-- Insert allowed!

-- अगर दूसरा user (id=2) try करे same title:
INSERT INTO event_table (organizer_id, title, event_date, status) 
VALUES (2, 'Hackathon 2025', '2026-04-20', 'pending');
-- Unique constraint: (2, 'Hackathon 2025', 2026-04-20) different है ✓
-- दूसरा organizer same title use कर सकता है!
```

---

### **Admin Approval Process - Final Validation**

```
┌──────────────────────────────┐
│ Event.status = 'pending'     │
│ organizer = Vicky (id=1)     │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ Admin Dashboard              │
│ Shows pending events         │
└────┬─────────────────────────┘
     │
     ▼
Admin decides: APPROVE/REJECT
     │
     ├─ APPROVE:
     │  Event.status = 'approved'
     │  Event.admin_approval = True
     │  Announcement बनता है: "Event approved!"
     │
     └─ REJECT:
        Event.status = 'rejected'
        rejection_reason = "Not appropriate"
        Announcement: "Event rejected. Reason: ..."
```

**Code Example:**

```python
# admin_panel/views.py (assumed)

@admin_required
def approve_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.status = 'approved'
    event.approved_by = request.user  # Admin who approved
    event.approved_at = timezone.now()
    event.save()
    
    # Organizer को notification भेजो
    Announcement.objects.create(
        created_by=request.user,  # Admin
        subject=f"Event '{event.title}' Approved!",
        message="Your event has been approved.",
        target_audience='organizers',
        event=event
    )
    return redirect('admin_dashboard')
```

---

### **Query Examples - How Data Flows**

**Example 1: Organizer अपने events देखता है**

```python
# organizer_app/views.py - Line 30
events = Event.objects.filter(organizer=request.user)

# SQL:
# SELECT * FROM event_table 
# WHERE organizer_id = 1 
# ORDER BY created_at DESC

# Results:
# Event.id=5, title="Hackathon", organizer_id=1 ✓
# Event.id=8, title="CodeSprint", organizer_id=1 ✓
# Event.id=12, title="Debate", organizer_id=2 ✗ (different organizer)
```

**Example 2: सभी events का count organizer-wise**

```python
# admin_panel/views.py (assumed)
from django.db.models import Count

organizer_stats = User.objects.annotate(
    event_count=Count('event')  # ← event__organizer से join
)

# SQL:
# SELECT user.id, user.username, COUNT(event.id) as event_count
# FROM user_table
# LEFT JOIN event_table ON user.id = event.organizer_id
# GROUP BY user.id, user.username

# Results:
# Vicky (id=1): event_count = 5
# Priya (id=3): event_count = 3
# Amar (id=5): event_count = 8
```

**Example 3: Pending events देखना (Admin के लिए)**

```python
# admin_panel/views.py (assumed)
pending_events = Event.objects.filter(status='pending').select_related('organizer')

# SQL:
# SELECT event.*, user.username, user.email
# FROM event_table
# INNER JOIN user_table ON event.organizer_id = user.id
# WHERE event.status = 'pending'
# ORDER BY event.created_at DESC

# Results लिए database से:
# Event.id=15, title="Workshop", organizer=Vicky (joined से name आया)
# Event.id=18, title="Seminar", organizer=Priya (joined से name आया)
```

---

## �🔗 RELATIONSHIPS VISUAL MAP

```
┌─────────────────────────────────────────────────┐
│                  USER TABLE                      │
│  (username, email, password, authentication)    │
└──────────┬────────────────────────────┬─────────┘
           │ 1-to-1             1-to-Many│
           │                            │
           ▼                            ▼
    ┌────────────────┐         ┌──────────────────┐
    │ USERPROFILE    │         │ EVENTREGISTRATION│
    │ (role info)    │         │ (registrations)  │
    └────────────────┘         └────────┬─────────┘
                                        │ Many-to-1
                                        ▼
                                ┌───────────────┐
                                │  EVENT TABLE  │
                                │ (event details)│
                                └───────┬───────┘
                                        │ 1-to-Many
                                        ▼
                        ┌───────────────────────────┐
                        │  CERTIFICATE TABLE        │
                        │ (awards & achievements)   │
                        └───────────────────────────┘

┌────────────────────┐
│ ANNOUNCEMENT TABLE │ ← Created by User
│ (communications)   │ ← Can be linked to Event
└────────────────────┘
```

---

## 🔄 DATA FLOW - HOW IT WORKS

### **1. Registration Flow**
```
Student (User) 
    ↓
Views Event 
    ↓
Clicks Register 
    ↓
Creates EventRegistration record
    ↓
Event.max_capacity check
    ↓
Team members added (if team event)
    ↓
Confirmation email sent
    ↓
Status = "registered"
```

### **2. Approval Flow** 
```
Organizer (User with organizer role)
    ↓
Creates Event
    ↓
Sets status = "pending"
    ↓
Admin views in dashboard
    ↓
Approves/Rejects
    ↓
Event status changes
    ↓
Organizer notified via Announcement
```

### **3. Certificate Flow**
```
Event ends
    ↓
Admin/Organizer marks Event.status = "completed"
    ↓
Batch job finds all EventRegistrations for this event
    ↓
For each student: Admin decides cert_type
    ↓
Certificate record created
    ↓
Certificate issued_date = today
    ↓
Student notified via Announcement
    ↓
Student can download/print
```

### **4. Announcement Distribution**
```
Creator (organizer/admin)
    ↓
Creates Announcement
    ↓
Sets priority & target_audience
    ↓
Publishes
    ↓
System filters: only relevant users see it
    ↓
Shown in dashboards
    ↓
Optional: Email notification sent
```

---

## 📈 RELATIONSHIP STATISTICS

| Relationship | Type | Example |
|------------|------|---------|
| User ↔ UserProfile | 1-to-1 | 1 user, 1 profile |
| User ↔ EventRegistration | 1-to-Many | 1 student, many registrations |
| User ↔ Certificate | 1-to-Many | 1 student, many certificates |
| User ↔ Event | 1-to-Many | 1 organizer, many events |
| User ↔ Announcement | 1-to-Many | 1 creator, many announcements |
| Event ↔ EventRegistration | 1-to-Many | 1 event, many students |
| Event ↔ Certificate | 1-to-Many | 1 event, many certificates |
| Event ↔ Announcement | 1-to-Many | 1 event, many announcements |
| EventRegistration → Certificate | 1-to-1 | After event completion |

---

## 🔑 KEY CONSTRAINTS

### **Unique Constraints**
- User.username - Har user ka unique login ID
- User.email - Har user ka unique email
- EventRegistration (student, event) - One registration per student per event
- Certificate.certificate_number - Unique certificate ID

### **NOT NULL Constraints**
- User: username, email, password
- UserProfile: user, role
- Event: organizer, title, event_date, status
- EventRegistration: student, event, registration_date
- Certificate: student, event, cert_type, issued_date
- Announcement: created_by, subject, message

### **Index Optimization**
```sql
CREATE INDEX idx_user_profile_role ON user_profile(role);
CREATE INDEX idx_event_status_date ON event(status, event_date);
CREATE INDEX idx_registration_student_event ON event_registration(student_id, event_id);
CREATE INDEX idx_certificate_student ON certificate(student_id);
CREATE INDEX idx_announcement_published ON announcement(is_published, published_date);
```

---

## 💡 PRACTICAL EXAMPLES

### **Example 1: Student Registration Path**
```
Vicky (User.id=1, role=student) 
  → Events page dekhleta hai
  → Hackathon 2025 (Event.id=5) click karta hai
  → Register button click
  → EventRegistration create: {student: Vicky, event: Hackathon, status: registered}
  → max_capacity check (50 < 100 ✓)
  → Confirmation: "You're registered!"
  → Event ka organizer ko announcement dikha namemidnight
```

### **Example 2: Certificate Award Path**
```
Hackathon 2025 ends (Event.event_date = April 16, 2026)
  → Admin marks Event.status = "completed"
  → System finds all EventRegistration.event_id = 5
  → Found: 47 registrations
  → Admin decides:
     - Ryan: cert_type = "winner_1" (1st place)
     - Priya: cert_type = "winner_2" (2nd place)
     - Amar: cert_type = "participant" (all others)
  → Certificate records created with certificate_number auto-generated
  → Students notified: "Check your certificates!"
```

### **Example 3: Announcement to Specific Audience**
```
Organizer (Nisha) creates Announcement:
  - subject: "Hackathon Rules Updated"
  - message: "Check competition guidelines..."
  - target_audience: "students"
  - event: Hackathon 2025
  → System publishes
  → Only USERS with EventRegistration.event = Hackathon 2025 see it
  → Role = "student" wale students ko dashboard notification
```

---

## ⚡ PERFORMANCE CONSIDERATIONS

**N+1 Query Prevention**:
```
❌ WRONG:
for registration in event_registrations:
    student = registration.student  # Extra query for each!
    
✅ RIGHT:
registrations = EventRegistration.objects.select_related('student', 'event')
for registration in registrations:
    student = registration.student  # Already loaded
```

**Indexing Strategy**:
- Student-based queries: Index on(student_id)
- Event-based queries: Index on (event_id, status)
- Date-based queries: Index on (event_date, created_at)
- Search queries: Index on (title, category)

**Pagination for Large Results**:
- Events list: 20 per page
- Registrations: 50 per page
- Certificates: 25 per page

---

**Created**: April 16, 2026
**Project**: College Events Management System
**Total Tables**: 6
**Total Relationships**: 12+
