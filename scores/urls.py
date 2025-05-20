from django.urls import path
from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.scores, name='scores'),
    path('add/', views.add_score, name='add_score'),
    path('edit/<int:score_id>/', views.edit_score, name='edit_score'),
    path('delete/<int:score_id>/', views.delete_score, name='delete_score'),
    path('subject/get_subjects/', views.get_subjects, name='get_subjects'),
    path('class/get_classes/', views.get_classes, name='get_classes'),
    path('student/get_students/', views.get_students, name='get_students'),
    path('manage/', views.manage_students, name='manage_students'),
    path('get-grades/', views.get_grades, name='get_grades'),
    path('manage/', views.manage_students, name='manage_students')
] 