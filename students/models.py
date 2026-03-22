from django.db import models
from users.models import MentoraBaseUser
from django_mongodb_backend.fields import ObjectIdAutoField

class Student(MentoraBaseUser):
    id = ObjectIdAutoField(primary_key=True)
    student_id = models.CharField(max_length=50)
    
    # This MUST be indented exactly like the fields above
    class Meta:
        db_table = 'users_student'
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['user']),
        ]