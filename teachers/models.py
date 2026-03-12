from django.db import models
from users.models import MentoraBaseUser
from django_mongodb_backend.fields import ObjectIdAutoField
from django.conf import settings

import random
import string

#Added By Saim Munshi: Selects stores all asccii and digit in ultimatestring and using random.choice to select 15 random character 
# genrating the code

def randomTeacherCodeGenerator():
    codeLength = 15
    ultimateString = string.ascii_letters + string.digits
    randomString = "" 
    for i in range(codeLength):
        randomString += random.choice(ultimateString)
    
    return randomString

###########################################################
class Teacher(MentoraBaseUser):
    id = ObjectIdAutoField(primary_key=True)
    license_number = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20, unique=True, default = randomTeacherCodeGenerator) #Added by Saim CourseCode
    
    class Meta:
        db_table = 'users_teacher'  # Custom collection name
    
    def __str__(self):
        return f"{self.full_name} (Teacher)"



#Added By Saim Munshi: Notfication mongodb object
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta:
        db_table = "teacher_notifications" 
    

    def __str__(self):
        return self.message
    
