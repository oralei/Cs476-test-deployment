from django.urls import path, include
from . import views           
from students import views as student_views 
from teachers import views as teacher_views 

urlpatterns = [
    path('', views.main_page_view, name="home"),
    path('teacher-Registration/', views.teacher_register_view, name='teacher_register_view'),
    path('student-Registration/', views.student_register_view, name='student_register_view'),
    path('login/', views.signin_page_view, name='signin_page_view'),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    
    path("logout/", views.logout_view, name="logout")
]