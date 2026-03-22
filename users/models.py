# courses/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django_mongodb_backend.fields import ObjectIdAutoField

"""# Added by Mark: This creates the blueprint for the entire Course and Task system backend.
"""
class CustomUser(AbstractUser):
    id = ObjectIdAutoField(primary_key=True) #mongo db compatiablity 
    # email must be unique for email also their username to work
    email = models.EmailField(unique=True) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # username is still required by Django but not for login

    @property
    def is_student(self):
        return hasattr(self, 'students_student_profile')

    @property
    def is_teacher(self):
        return hasattr(self, 'teachers_teacher_profile')

# Abstract Base Class (Parent class for Student and Teacher model)
# See teachers/models.py or students/models.py
class MentoraBaseUser(models.Model):
    # We reference the CustomUser via settings to avoid circular imports
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_profile"
    )
    full_name = models.CharField(max_length=255)
    profile_image_url = models.URLField(max_length=500, null=True, blank=True)
    
    class Meta:
        abstract = True