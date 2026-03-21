from django.urls import path
from . import views  # This only imports from the teachers app

urlpatterns = [
    path('home/', views.teacherHome, name='teacher_home'),

    # Course URLs (Added by Mark)
    path('courses/', views.teacherCourseList, name='teacher-course-list'),
    path('courses/create-course', views.teacherCreateCourse, name='create-course'),
    path('courses/<str:course_id>/', views.teacherCourseMain, name='teacher-course-main'),
    
    path('needs-feedback/', views.teacherNeedsFeedbackList, name='needs-feedback-list'),
    
    # Note: This is required for specific task pages
    path('tasks/<str:task_id>/submissions/', views.teacherTaskSubmissions, name='teacher-task-submissions'),
    path('submissions/<str:submission_id>/feedback/', views.teacherFeedback, name='teacher-feedback'),

    # Notification URL (Added by Saim)
    path('notifications/read/<str:notification_id>/', views.markNotificationAsRead, name='teacher-notif-read'),
    
    path('my-students/', views.My_Student, name='My_Student'), #Added by Saim Connection to my student page

    # Note: Edit and Delete Course url path
    path('courses/edit-course/<str:course_id>/', views.editCourse, name='edit-course'), # Added By Saim Connect to create course with course id of exisiting course to allow user
    path('delete-course/<str:course_id>/', views.deleteCourse, name='delete-course'),  # Added By Saim Connect to delete course

    # Note: Edit and Delete Task url path
    path('tasks/edit-task/<str:task_id>/', views.editTask, name='edit-task'), # Added By Saim Connect to create course with course id of exisiting course to allow user
    path('delete-task/<str:task_id>/', views.deleteTask, name='delete-task'),  # Added By Saim Connect to delete task


    path('calendar/', views.Calendar, name='calendar'),

    # Added by win516
    path('progress/', views.Progress, name='teacher_progress'),
]