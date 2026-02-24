from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
# ==========================================
# 1. FOYDALANUVCHI PROFILLI (O'quvchilar)
# ==========================================


class Profile(models.Model):
    login = models.CharField(max_length=50, unique=True, verbose_name="Login")
    password = models.CharField(max_length=128, verbose_name="Parol")
    full_name = models.CharField(max_length=255, verbose_name="Ism-Familiya")
    active_title = models.CharField(max_length=100, blank=True, null=True, default="Yangi foydalanuvchi")
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name="Profil rasmi")
    razryad = models.CharField(max_length=20, verbose_name="O'quvchi darajasi")
    points = models.IntegerField(default=0, verbose_name="XP Ballari")

    sinf = models.CharField(max_length=10, verbose_name="Sinf")
    parallel = models.CharField(max_length=5, verbose_name="Sinf harfi")

    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="O'quvchi telefoni")
    parent_phone = models.CharField(max_length=20, verbose_name="Ota-ona telefoni")
    mahalla = models.CharField(max_length=255, verbose_name="Mahalla")
    kocha = models.CharField(max_length=255, verbose_name="Ko'cha")
    uy = models.CharField(max_length=50, verbose_name="Uy raqami")

    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    is_active = models.BooleanField(default=False, verbose_name="Tasdiqlangan")
    created_at = models.DateTimeField(auto_now_add=True)
    is_teacher = models.BooleanField(default=False)



    def __str__(self):
        return f"{self.full_name} ({self.sinf}-{self.parallel})"

# ==========================================
# 2. O'QITUVCHILAR VA FANLAR
# ==========================================
class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Fan nomi")
    teacher_user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})

    def __str__(self): return self.name

class Teacher(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="F.I.O")
    image = models.ImageField(upload_to='teachers/', blank=True, null=True, verbose_name="Rasmi")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, verbose_name="Fani")
    bio = models.TextField(blank=True, verbose_name="Ma'lumot")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")


    def __str__(self): return self.full_name

    class Meta:
        verbose_name = "O'qituvchi"
        verbose_name_plural = "O'qituvchilar"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    subject_name = models.CharField(max_length=100)
    class_leader = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=20)
    address_mahalla = models.CharField(max_length=100)
    address_street = models.CharField(max_length=100)
    address_home_number = models.CharField(max_length=20)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self): return self.full_name

# ==========================================
# 3. REELS VA IJTIMOIY TIZIM
# ==========================================

# ==========================================
# 4. CHAT TIZIMI
# ==========================================
class Message(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    text = models.TextField(blank=True, null=True)
    voice = models.FileField(upload_to='chat_voices/', blank=True, null=True)
    group_name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

# ==========================================
# 5. TA'LIM: TEST, VAZIFA, LOYIHA
# ==========================================
class TeacherTest(models.Model): # Nomini TeacherTest qildik
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    questions = models.TextField() # JSON formatda saqlash tavsiya etiladi
    correct_answers = models.TextField()
    sinf = models.CharField(max_length=10)
    parallel = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title


class TestResult(models.Model):
        student = models.ForeignKey(Profile, on_delete=models.CASCADE)
        test = models.ForeignKey(TeacherTest, on_delete=models.CASCADE)
        score = models.IntegerField()
        date = models.DateTimeField(auto_now_add=True)
        created_at = models.DateTimeField(default=timezone.now)
        # TestResult ichida questions_data bo'lishi shart emas (ixtiyoriy)

class Homework(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='homeworks')
    sinf = models.CharField(max_length=10)
    parallel = models.CharField(max_length=5)
    teacher_user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class HomeworkStatus(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='statuses')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)  # "Bajardim" uchun
    needs_help = models.BooleanField(default=False)  # "Tushunmadim" uchun
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('homework', 'student')

class ProjectWork(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='projects/pdfs/')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    members_info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# ==========================================
# 6. KUTUBXONA VA DO'KON
# ==========================================
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, blank=True, null=True)
    count = models.PositiveIntegerField(default=1)
    image_url = models.URLField(blank=True, null=True)
    price = models.IntegerField(default=0, verbose_name="Narxi (XP)")

    def __str__(self):
        return self.title

class Order(models.Model):
    student = models.ForeignKey('Profile', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    return_deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Kutilmoqda')
    is_given = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.return_deadline:
            # 7 kunlik muddatni avtomatik belgilash
            self.return_deadline = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name} - {self.book.title} ({self.status})"

# ==========================================
# 7. YUTUQLAR VA BOSHQA
# ==========================================

class Notification(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"{self.user.login}: {self.text[:20]}"
class ClassMessage(models.Model):
    sinf = models.CharField(max_length=10)
    parallel = models.CharField(max_length=10)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
from django.utils import timezone

class Attendance(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    is_absent = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.date} (Kelmadi)"
class Schedule(models.Model):
    DAYS = [
        ('Dushanba', 'Dushanba'),
        ('Seshanba', 'Seshanba'),
        ('Chorshanba', 'Chorshanba'),
        ('Payshanba', 'Payshanba'),
        ('Juma', 'Juma'),
        ('Shanba', 'Shanba'),
    ]
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    sinf = models.CharField(max_length=10) # Masalan: 8
    parallel = models.CharField(max_length=5) # Masalan: A
    day = models.CharField(max_length=20, choices=DAYS)
    subjects_list = models.TextField(help_text="Darslarni vergul bilan kiriting")

    class Meta:
        unique_together = ('teacher', 'sinf', 'parallel', 'day')
class Competition(models.Model):
    title = models.CharField(max_length=255)
    # O'qituvchi yaratgan test bilan bog'liqlik
    test = models.ForeignKey('TeacherTest', on_delete=models.CASCADE, related_name='competitions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
