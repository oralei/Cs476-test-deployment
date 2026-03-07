from django.db import models
from users.models import MentoraBaseUser
from django_mongodb_backend.fields import ObjectIdAutoField

class Teacher(MentoraBaseUser):
    id = ObjectIdAutoField(primary_key=True)
    license_number = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'users_teacher'  # Custom collection name
    
    def __str__(self):
        return f"{self.full_name} (Teacher)"
