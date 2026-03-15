from django.urls import path
from . import views  # This only imports from the teachers app

urlpatterns = [
    path('home/', views.teacherHome, name='teacher_home'),

    # Course URLs (Added by Mark)
    path('courses/', views.teacherCourseList, name='teacher-course-list'),
    path('courses/create-course', views.teacherCreateCourse, name='create-course'),
    path('courses/<str:course_id>/', views.teacherCourseMain, name='teacher-course-main'),
    path('courses/edit-course/<str:course_id>/', views.editCourse, name='edit-course'),  # Added by Saim
    path('delete-course/<str:course_id>/', views.deleteCourse, name='delete-course'),  # Added by Saim

    # Task URLs (Added by Mark)
    path('create-task/', views.Create_Task, name='create-task'),
    path('tasks/<str:task_id>/submissions/', views.teacherTaskSubmissions, name='teacher-task-submissions'),
    path('submissions/<str:submission_id>/feedback/', views.teacherFeedback, name='teacher-feedback'),

    # Notification URL (Added by Saim)
    path('notifications/read/<str:notification_id>/', views.markNotificationAsRead, name='teacher-notif-read'),

    # Other pages
    path('my-students/', views.My_Student, name='My_Student'),  # Added by Saim
    path('calendar/', views.Calendar, name='calendar'),

    # Added by win516
    path('progress/', views.Progress, name='teacher_progress'),
]