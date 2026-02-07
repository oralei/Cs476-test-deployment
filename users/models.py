from django.db import models

# Create your models here.
from django.db import models

# This is a template; it won't create its own collection
class MentoraBaseUser(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    profile_image_url = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        abstract = True # This is the magic line that keeps things separate

# This will create a 'students' collection in Atlas
class Student(MentoraBaseUser):
    student_id = models.CharField(max_length=50)

# This will create a 'teachers' collection in Atlas
class Teacher(MentoraBaseUser):
    license_number = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)