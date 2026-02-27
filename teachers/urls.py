from django.urls import path
from . import views  # This only imports from the teachers app

urlpatterns = [
    # If you have teacherHome in teachers/views.py:
    path('home/', views.teacherHome, name='teacher_home'),
]