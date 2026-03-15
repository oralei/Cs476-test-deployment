from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.studentHome, name='student_home'),
    path('calendar/', views.Calendar, name='student-calendar'),
    path('mentor/', views.Mentor, name='mentor'),
    path('progress/', views.Progress, name='progress'),

    # Course URLs (Added by Mark)
    path('course-browser/', views.courseBrowser, name='course-browser'),
    path('my-courses/', views.myCourses, name='my-courses'),
    path('course/<str:course_id>/', views.studentCourseMain, name='student-course-main'),

    # Hidden path just for processing the 'Join' button POST request
    path('course/<str:course_id>/join/', views.joinCourse, name='join-course'),
    # Hidden path just for processing the 'Leave' button POST request
    path('course/<str:course_id>/leave/', views.leaveCourse, name='leave-course'),

    # Task URLs (Added by Mark)
    path('tasks/', views.studentTasks, name='student-tasks'),
    path('tasks/<str:task_id>/', views.studentTaskSubmit, name='student-task-submit'),

    # Notification URL
    path('notifications/read/<str:notification_id>/', views.markNotificationAsRead, name='student-notif-read'),
]