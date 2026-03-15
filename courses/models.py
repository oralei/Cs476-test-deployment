# courses/models.py
from django.db import models
from django.conf import settings
from django_mongodb_backend.fields import ObjectIdAutoField

import random
import string

# Function: Creates a randomly generated code 
def randomCodeGenerator():
    codeLength = 15
    ultimateString = string.ascii_letters + string.digits
    randomString = "" 
    for i in range(codeLength):
        randomString += random.choice(ultimateString)
    
    return randomString

# Added by Mark: This creates the blueprint for the entire Course and Task system backend.

# Class: Course (MongoDB collection = courses_course)
# The main overarching object blueprint for a Course.
#
#
class Course(models.Model):
  id = ObjectIdAutoField(primary_key=True)
  title = models.CharField(max_length=200)
  description = models.TextField()
  max_students = models.PositiveIntegerField()
  course_code = models.CharField(max_length=20, unique=True, default = randomCodeGenerator)

  private = models.BooleanField(default=False)

  # RELATIONS
  teacher = models.ForeignKey(
  	'teachers.Teacher', 
    on_delete=models.CASCADE,
    related_name='courses'
  )
  students = models.ManyToManyField(
    'students.Student',
    related_name='enrolled_courses',
    blank=True
  )
  
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.title

# Class: Task (MongoDB collection = courses_task)
# 
#
#
class Task(models.Model):
  id = ObjectIdAutoField(primary_key=True)
  course = models.ForeignKey(
    Course, 
    on_delete=models.CASCADE, 
    related_name='tasks'
  )
  
  title = models.CharField(max_length=200)
  description = models.TextField()
  start_date = models.DateTimeField(null=True, blank=True)
  due_date = models.DateTimeField(null=True, blank=True)
  points_possible = models.IntegerField(default=100) # Might be removed, don't need grading.
  assigned_students = models.ManyToManyField(
      'students.Student',
      related_name='assigned_tasks',
      blank=True
  )
  
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.title} ({self.course.title})"

# Class: TaskSubmission (MongoDB collection = courses_tasksubmission)
# Represents the student's actual uploaded submission (the file or answer).
#
#
class TaskSubmission(models.Model):
  id = ObjectIdAutoField(primary_key=True)
  
  task = models.ForeignKey(
		Task, 
		on_delete=models.CASCADE,
		related_name='submissions'
  )
  student = models.ForeignKey(
		'students.Student', 
		on_delete=models.CASCADE,
		related_name='submissions'
  )
  
  # The content of the submission
  submission_text = models.TextField(blank=True) 
  file_url = models.URLField(blank=True) # If they upload a file

  # Django char fields are tuples
  STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('reviewed', 'Reviewed'),
  ]
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
  
  submitted_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
      # Ensures a student can only submit ONCE per task
      # If they submit again, they should update this existing record
      unique_together = ('task', 'student')

  def __str__(self):
      return f"Submission: {self.student} - {self.task.title}"

# Class: TaskFeedBack (MongoDB collection = courses_taskfeedback)
# Represents the teacher's grading and comments.
#
#
class TaskFeedback(models.Model):
  id = ObjectIdAutoField(primary_key=True)
  
  # OneToOne because one submission has exactly one feedback/grade
  submission = models.OneToOneField(
      TaskSubmission,
      on_delete=models.CASCADE,
      related_name='feedback' # Access via: submission.feedback
  )
  
  grade = models.FloatField() # Might be removed, don't need grading.
  comments = models.TextField(blank=True) # Example: "Great job, but check spelling."
  
  graded_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Feedback for {self.submission}"
  
# Class: Notification (MongoDB collection = courses_notification)
# Used in the Observer Pattern
#
#
class Notification(models.Model):
  id = ObjectIdAutoField(primary_key=True) 
  # Link it to the user receiving the notification (Teacher or Student)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
  notification_type = models.CharField(max_length=50)
  message = models.CharField(max_length=255)
  is_read = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return f"Notification for {self.user}: {self.message}"