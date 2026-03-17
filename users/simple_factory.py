# simple_factory.py

from django.contrib.auth import get_user_model
from students.models import Student
from teachers.models import Teacher

User = get_user_model()

class UserRegistrationFactory:
    """
    Implements the Simple Factory Pattern for User Registration.
    Matches the SimpleFactory -> User CreateUser(type) from your UML Diagram.
    """
    
    @staticmethod
    def register_user(user_type: str, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        name = kwargs.get('name')
        image_url = kwargs.get('image_url')

        # 1. Create the base User model shared by both
        user = User.objects.create_user(
            username=name,
            email=email, 
            password=password
        )

        # 2. Create the Concrete Product (Student or Teacher)
        if user_type == 'student':
            profile = Student.objects.create(
                user=user,
                full_name=name,
                student_id=kwargs.get('student_id'),
                profile_image_url=image_url
            )
        elif user_type == 'teacher':
            profile = Teacher.objects.create(
                user=user,
                full_name=name,
                license_number=kwargs.get('license_number'),
                specialization=kwargs.get('specialization'),
                profile_image_url=image_url
            )
        else:
            # Fallback for unsupported types
            raise ValueError(f"Invalid user_type: {user_type}")

        return user, profile