from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.studentHome, name='student_home'),
    path('calender/', views.Calender, name='calender'),
    path('mentor/', views.Mentor, name='mentor'),
    path('progress/', views.Progress, name='progress'),
    path('courses/', views.Courses, name='Courses'),
]