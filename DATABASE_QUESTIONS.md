# Database Tables - 20 Industry Level Interview Questions (Hinglish)

---

## 🏆 20 INDUSTRY-LEVEL SAWAAL (Database Tables ke liye)

### 1. **User aur UserProfile tables mein 1-to-1 relationship kyon important hai?**
Django ka User table authentication handle karta hai, jabki UserProfile college-specific data (role, enrollment number, branch) store karta hai। 1-to-1 relationship ensure karta hai ki har user ka ek profile hota hai aur data duplication nahi hota।

### 2. **UNIQUE constraint Event + registration_date par rakhne ke bajaaye (student, event) par kyon rakhte hain?**
Kyunki ek student ek same event mein multiple times register nahi kar sakta, chahe kisi bhi date par registration ho। (student, event) unique constraint duplicate registrations prevent karta hai। Event + registration_date par constraint se same student same event mein alag-alag times register kar sakta tha jo wrong hai।

### 3. **Event.status field mein pending, approved, rejected, completed values have, to cancellation kaise handle karoge?**
Cancelled status add kar sakte hain Event model mein। When event cancelled ho, system automatically EventRegistrations cancel karega aur students ko refund/notification bhejega। Cancelled events dashboards par highlight honge।

### 4. **Certificate kab automatic generate hona chahiye aur kab admin manually create kare?**
Simple participation certificates event completion ke baad automated generate ho sakte hain (status = "completed" par)। Lekin winner certificates admin manual decide kare kyunki judging criteria event-specific hote hain। Hybrid approach best practice hai।

### 5. **EventRegistration mein team_members ko JSON format mein store karna chahiye ya separate TeamMembers table banana chahiye?**
Large scale par separate TeamMember table banana chahiye (Many-to-Many relationship)। Lekin college events like codebase mein simple JSON adequate hai। Scalability requirement ke basis par decide karna। JSON easier but limited, separate table flexible and queryable।

### 6. **Race condition kaise prevent karoge jab 50 max_capacity wale event mein simultaneously 100 students register karte hon?**
Database-level UNIQUE constraint + transaction-level locking use karna chahiye। `SELECT FOR UPDATE` query kar sakte hain registration se pehle capacity check karne ke liye। Celery task queue mein registrations process kar sakte hain serialized order mein।

### 7. **Announcement model mein expiry_date keep karte hain, to stale announcements auto-delete kaise hoga?**
Celery Beat scheduled task create kar sakte hain jo daily database cleanup kare। Alternatively, query mein `expiry_date > NOW()` filter add kar sakte hain। Soft delete approach better hai (is_deleted flag) audit trail keep karne ke liye।

### 8. **User role (admin, organizer, student) ko UserProfile mein CharField se store karte ho, Django Groups use kyon nahi karte?**
Django Groups permission management ke liye better hain। But College Events mein simple role-based access chal raha hai। Scalability mein Groups migrate kar sakte hain (role CharField + Groups dono use kar sakte hain)। Ek transition phase ho sakta hai।

### 9. **Event capacity full ho gaya, waiting list kaise implement karoge?**
Separate WaitlistRegistration table create kar sakte hain (same structure) या EventRegistration mein status="waitlist" add kar sakte hain। Jab koi student cancel kare to waitlist ka pehla person auto-approve ho ja sakta hai। FIFO queue maintain karna padega।

### 10. **Certificate.certificate_number auto-generate karoge, UUID use karoge ya sequential number?**
UUID better hai uniqueness guarantee aur non-sequential hone se guessing prevent hoti hai। `uuid.uuid4().hex[:12]` like format use kar sakte hain। Sequential number simple print proof mein number likhne ke liye, UUID verification aur traceability ke liye।

### 11. **User logout karte hain aur last_login field update na ho, to user tracking kaise hogi?**
last_login field only login time record karta hai। Activity tracking ke liye separate AuditLog table banana chahiye jo har action (login, register, etc) ki timestamp rakhe। Google Analytics like tool bhi use kar sakte analysis ke liye।

### 12. **Event mein registration_fee field hai, to payment status track kaise karoge?**
EventRegistration mein payment_status field add karna chahiye (unpaid, pending, paid, failed)। Separate Payment table better hai transaction details store karne ke liye (payment_id, gateway, amount, timestamp)। Payment response webhook handle karna padega।

### 13. **Organizer ne event create kiya, admin ne reject kiya, organizer edit karke dobara submit karenage, versioning kaise handle karoge?**
Event model mein version field add kar sakte hain (v1, v2, v3)। Ya EventVersion table create kar sakte hain jo historical changes track kare। Rejection reason store karne ke liye rejection_reason field add kare।

### 14. **Student ne team event ke liye register kiya, team members cancel karte ho, registration automatic cancel hona chahiye ya pending ho?**
Team mein sirf leader cancel kar sakta hai (organizer-level change)। Individual team member opt-out kar le to team size reduce hogi but registration valid rehegi। Leader complete team remove kar sakta hai then registration cancel।

### 15. **Batch mein 1000 certificates generate karte hain, N+1 query problem kaise avoid karoge?**
`Certificate.objects.select_related('student', 'event').batch_create()` use kar sakte hain। Alternatively `bulk_create()` use karke database hits minimize kar sakte hain। Query optimization tools (django-debug-toolbar) se verify karna important hai।

### 16. **Announcement target_audience ka "all" vs "students" logic mein, checking optimize kaise karoge?**
Database query mein `target_audience = 'all' OR (target_audience = 'students' AND user.role = 'student')` filter kar sakte hain। Alternatively caching layer (Redis) use kar sakte hain frequently accessed announcements ke liye। Query indexing important hai।

### 17. **EventRegistration status "no_show" mark karte hain, certificate kaise handle karoge?**
No-show students ko certificates nahi dena chahiye। Certificate generation logic mein status = "attended" condition add karna चाहिए। Alternatively attendance flag EventRegistration में add कर सकते हैं।

### 18. **User delete karte hain, cascade kaise handle karoge (User → UserProfile, EventRegistration, Certificate)?**
ON DELETE CASCADE use kar sakte hain quick cleanup ke liye। Lekin production mein soft delete better hai (is_deleted flag + trigger)। Historical data audit trail important hai।

### 19. **Event search karte ho (title, category, date range), database indexing strategy kya hoga?**
Composite index बना सकते हैं: `CREATE INDEX idx_event_search ON event(category, event_date, status)`। Title के लिए FULLTEXT search index। Date range queries के लिए event_date पर B-tree index काफी है।

### 20. **UserProfile mein profile_picture store कर रहे हो, media management कैसे करोगे (storage, CDN, cleanup)?**
Production में AWS S3 या CloudFront use करो media serving के लिए। Unused images को periodically clean करने के लिए Celery task set करो। Image optimization (thumbnail generation) करो storage save करने के लिए।

---

## 📊 Topic-wise Distribution

| Topic                             | Questions                      | Difficulty |
|-----------------------------------|--------------------------------|------------|
| **Relationships**                 | Q1, Q5, Q12                    | Medium     |
| **Constraints & Data Integrity**  | Q2, Q6, Q14, Q18               | Hard       |
| **Scaling & Performance**         | Q7, Q10, Q15, Q19              | Hard       |
| **Feature Implementation**        | Q3, Q8, Q9, Q11, Q13, Q16, Q17 | Hard       |
| **Infrastructure & Optimization** | Q4, Q20                        | Hard       |

---

## 🔑 Key Concepts Covered

✅ **Database Design**: 1-to-1, 1-to-Many relationships
✅ **Constraints**: UNIQUE, NOT NULL, Foreign Keys
✅ **Data Integrity**: Race conditions, validation
✅ **Performance**: N+1 queries, indexing, caching
✅ **Scalability**: Batch operations, async processing
✅ **Security**: Soft deletes, audit trails
✅ **Feature Design**: Waitlists, versioning, cascading
✅ **Infrastructure**: Media management, CDN, storage

---

## 💡 Interview Tips

1. **Draw ER diagrams** जब relationship questions पूछे जाएं
2. **Performance implications** discuss करो हर design decision के लिए
3. **Trade-offs explain** करो (e.g., JSON vs separate table)
4. **Real-world examples** दो अपनी experience से
5. **Scalability** mention करो हर solution में

---

**Total Questions**: 20
**Difficulty Level**: Industry/Senior
**Project**: College Events Management System
**Created**: April 16, 2026
