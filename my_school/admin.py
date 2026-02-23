from django.contrib import admin
from .models import (
    Profile, Subject, Teacher, TeacherProfile, TeacherReels,
    Post, Comment, Video, Message, TeacherTest, TestResult,
    Homework, HomeworkStatus, ProjectWork, Book, Order, Notification, VideoComment,
    ClassMessage, Attendance, Schedule
)

# 1. Profile (O'quvchilar)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('login', 'full_name', 'sinf', 'parallel', 'points', 'is_active')
    list_filter = ('sinf', 'parallel', 'is_active')
    search_fields = ('login', 'full_name')
    list_per_page = 20

# 2. O'qituvchilar va Fanlar
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher_user')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'subject_name', 'class_leader', 'phone')
    search_fields = ('full_name', 'class_leader')

# 3. Kutubxona va Buyurtmalar (Xatolik tuzatilgan qism)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'count', 'price')
    list_editable = ('count', 'price')
    search_fields = ('title', 'author')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 'book_name' o'rniga 'book' va 'is_returned' o'rniga 'status' ishlatildi
    list_display = ('student', 'book', 'order_date', 'status')
    list_filter = ('status', 'order_date')
    list_editable = ('status',)

# 4. Dars Jadvali
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('day', 'sinf', 'parallel', 'teacher')
    list_filter = ('day', 'sinf', 'parallel')
    search_fields = ('subjects_list',)


# 6. Vazifalar va Testlar
@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'sinf', 'parallel', 'created_at')

@admin.register(TeacherTest)
class ClassTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'sinf', 'parallel')

# 7. Ijtimoiy va Chat (Qisqa ko'rinishda)
admin.site.register(Post)
admin.site.register(Video)
admin.site.register(Message)
admin.site.register(ClassMessage)
admin.site.register(Attendance)
admin.site.register(Notification)