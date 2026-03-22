from django.urls import path
from django.contrib.auth import views as auth_views
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

    # Matthew: Feedback url routing
    path('feedback/', views.student_feedback, name='student_feedback'),
    path('mark-feedback-read/<str:feedback_id>/', views.mark_feedback_read, name='mark_feedback_read'),
    path('archive-feedback/<str:feedback_id>/', views.archive_feedback, name='archive_feedback'),

    # Added by Stephen:
    path('settings/', views.studentSettings, name='student-settings'),
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='password_change.html'),
         name='password_change'),

    path('password-change-done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='password_change_done.html'),
         name='password_change_done'),
]