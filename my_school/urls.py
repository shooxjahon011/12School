from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import view_projects_view



urlpatterns = [
    # 1. Kirish va Ro'yxatdan o'tish
    path('', views.login, name='login'),
    path('register/', views.signup, name='signup'),
    path('verify-code/', views.verify_code_view, name='verify_code'),


    path('second/', views.second_view, name='second_page'),
    path('add-student/', views.add_student_view, name='add_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('create-test/', views.create_test_view, name='create_test'), # Shuni qo'shing!
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('view-projects/', view_projects_view, name='view_projects'),

    # 5. Dashboard bo'limlari (Nomlarni (name) to'g'irladim)
    path('subjects/', views.subjects_view, name='subjects'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_user'),
    path('projects/', views.submit_project_view, name='projects'), # name tahrirlandi
    path('chat/', views.chat_view, name='chat'),
    path('teacher-registration-save/', views.teacher_registration_save, name='teacher_reg_save'),
    path('teacher-homeworks/', views.teacher_homeworks, name='teacher_homeworks'),
    path('teacher-schedule/', views.teacher_schedule, name='teacher_schedule'),
    path('student-schedule/', views.student_schedule, name='student_schedule'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('compete/', views.student_test_list, name='student_test_list'), # O'quvchi testlar ro'yxati
    path('solve-test/<int:test_id>/', views.solve_test_view, name='solve_test'),
    path('librarian-dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('confirm-book/<int:order_id>/', views.confirm_book_give, name='confirm_book_give'),

    # 6. O'qituvchi va Ta'lim tizimi
    path('teacher-registration/', views.teacher_reg_view, name='teacher_reg'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('give-homework/', views.give_homework_view, name='give_homework'),
    path('subjects/<int:subject_id>/', views.homework_detail_view, name='homework_detail'),
    path('update-hw/<int:hw_id>/<str:action>/', views.update_homework_status, name='update_hw'),
    path('save-test/', views.save_test_view, name='save_test'),
    path('compete/', views.compete_view, name='compete'),
    path('start-test/<int:test_id>/', views.start_test_view, name='start_test'),
    path('check-test/<int:test_id>/', views.check_test_view, name='check_test'),
    path('send-help-request/<int:teacher_id>/', views.send_help_request, name='send_help'),
    path('teacher-homeworks/', views.teacher_homeworks, name='teacher_homeworks'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('add-student/', views.add_student_view, name='add_student'),
    path('delete-student/<int:std_id>/', views.delete_student, name='delete_student'),
    path('homework-action/<int:hw_id>/<str:action_type>/', views.student_action, name='student_action'),
    path('schedule/', views.teacher_schedule, name='schedule'),

    # --- Profil va Yutuqlar ---
    path('teacher-profile/', views.teacher_profile, name='teacher_profile'),

    # 7. Kutubxona
    path('library/', views.library_view, name='library'),
    path('library/add/', views.add_book_view, name='add_book'),
    path('library/order/<int:book_id>/', views.place_order, name='place_order'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
