"""
URL configuration for Cs476GroupProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import teacher_register_view # connects the views function that returns the register_view
from users.views import student_register_view 
 #connects the views function that returns the main_page_view
from users.views import signin_page_view #connects the views function that returns the login_page_view

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    
    # Added by Mark: Separated student and teacher registration pages
    #path('student-register/', student_register_view, name ="student-register"),
    #path("teacher-register/", teacher_register_view, name="teacher-register"),

    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),  # Fixed by win516: removed duplicate
    path('users/', include('users.urls')),
    
    # Note by Mark: Add this once teachers/urls.py is made and ready
    # path('teachers/', include('teachers.urls'))
    
    # Any URL starting with 'accounts/' will be handled by users.urls
    # Note from Mark: Not sure exactly how this pathing works, but URLS will have /accounts/ in it via Django authentication
    
]

"""
    path('admin/', admin.site.urls),
    path('', main_page_view, name="home"),
    path('register/student/', student_register_view, name='student_register_view'),
    path('register/teacher/', teacher_register_view, name='teacher_register_view'),
    path('login/', signin_page_view, name='signin_page_view'),
    path('student/home/', studentHome, name='student_home'),
    path('teacher/home/', teacherHome, name='teacher_home'),
    path('student/Courses/', Courses, name='Courses'),
    """