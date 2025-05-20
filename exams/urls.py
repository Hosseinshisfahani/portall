from django.urls import path, re_path
from . import views

app_name = 'exams'

urlpatterns = [
    # User routes
    path('', views.exam_list, name='exam_list'),
    path('simple/', views.simple_exam_list, name='simple_exam_list'),
    path('<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('my-exams/', views.my_exams, name='my_exams'),
    path('take/<int:registration_id>/', views.take_exam, name='take_exam'),
    path('take/<int:registration_id>/<int:question>/', views.take_exam, name='take_exam_with_question'),
    path('answer/<int:registration_id>/<int:question_id>/', views.view_answer, name='view_answer'),
    path('view-answer/<int:registration_id>/<int:question_id>/', views.view_answer_direct, name='view_answer_direct'),
    path('complete/<int:registration_id>/', views.complete_exam, name='complete_exam'),
    
    # Admin routes
    path('admin/manage/', views.manage_exams, name='manage_exams'),
    path('admin/registrations/', views.manage_registrations, name='manage_registrations'),
    path('admin/registration/<int:registration_id>/update/', views.update_registration_status, name='update_registration_status'),
    path('admin/import-questions/', views.import_questions, name='import_questions'),
    
    # Debug route
    path('debug/', views.debug_view, name='debug_view'),
] 