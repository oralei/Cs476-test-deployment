from django.shortcuts import render, redirect
import cloudinary
import cloudinary.uploader
from django.contrib import messages
from django.urls import reverse_lazy
from students.models import Student
from teachers.models import Teacher
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout

#from django.contrib.auth import get_user_model
#from django.contrib.auth import authenticate, login
#from teachers.models import Teacher
#from django.contrib.auth.models import update_last_login
#from django.contrib.auth.signals import user_logged_in
import re


# Create your views here.
"""
Author: Saim Munshi
Name Function: register_view
type: Function 
Purpose: direct view.py django to the correct html file
"""

def main_page_view(request):
    return render(request, 'MainHome.html')






"""
Author: Saim Munshi
Function Name: student_register_view
Purpose: direct view.py django to the correct html file
Update: Fixed Cloudinary-MongoDB picture upload - Mark
"""
# Get the active User model (CustomUser)
User = get_user_model() # make sure it uses the custom user configuration 

def student_register_view(request):
    if request.method == 'POST':
        # Print all data received - Used to debug and test if POST data is being sent.
        print(f"Data: {request.POST}")
        
        # Check for file
        image_url = None
        image_file = request.FILES.get('UploadPFP')
        if image_file:
            try:
                upload_result = cloudinary.uploader.upload(
                    image_file, 
                    folder="Mentora_Profiles"
                )
                image_url = upload_result.get('secure_url')
                print(f"Student Register: Cloudinary Success: {image_url} ---")
            except Exception as e:
                print(f"Student Register: Cloudinary Error: {e} ---")
        else:
            print("Student Register: No image file provided")

        # Set user data with POST data
        email = request.POST.get('email')
        password = request.POST.get('mainpassword')
        confirmpassword = request.POST.get('confirmpassword')
        name = request.POST.get("name", "").strip()


        #Regex to ensure the name and las
        name_regex = r"^[A-Za-z]+(?: [A-Za-z'-]+)+$"
        if not name: 
            messages.error(request, "Full name is required.")
            return render(request, "StudentRegistration.html")
        
        if not re.match(name_regex, name):
            messages.error(request, "Full name is Required")
            return render(request, "StudentRegistration.html")

        if User.objects.filter(email=email).exists():
            print("Student Register: User already exists ---")
            return render(request, 'StudentRegistration.html', {'error': 'Email already exists'})
        
        # Password authentication
        if password != confirmpassword:
            messages.error(request, "Password do not match.")
            return render(request, "StudentRegistration.html")
        

        #Email authentication
        if User.objects.filter(email=email).exists(): 
            messages.error(request, "Email already exists.") 
            return render(request, "StudentRegistration.html")
        
        try:
            # Create User
            user = User.objects.create_user(
                username=request.POST.get('name'),  # Changed from email to name
                email=email, 
                password=password
            )

   
            student = Student.objects.create(
                user=user,
                full_name=request.POST.get('name'),
                student_id=request.POST.get('studentId'),
                profile_image_url=image_url
            )
            

            # Auto Login
            login(request, user)
            return redirect('signin_page_view') # Note: url names use underscore. See student/urls.py
        

        except Exception as e:
            print(f"--- CRITICAL ERROR DURING SAVE: {e} ---")
            return render(request, 'StudentRegistration.html', {'error': str(e)})

    return render(request, 'StudentRegistration.html')




def teacher_register_view(request):
    if request.method == 'POST':
        # Print all data received - Used to debug and test if POST data is being sent.
        print(f"Data: {request.POST}")
        
        # Check for file
        image_url = None
        image_file = request.FILES.get('UploadPFP')
        if image_file:
            try:
                upload_result = cloudinary.uploader.upload(
                    image_file, 
                    folder="Mentora_Profiles"
                )
                image_url = upload_result.get('secure_url')
                print(f"Student Register: Cloudinary Success: {image_url} ---")
            except Exception as e:
                print(f"Student Register: Cloudinary Error: {e} ---")
        else:
            print("Student Register: No image file provided")

        # Set user data with POST data
        email = request.POST.get('email')
        password = request.POST.get('mainpassword')
        confirmpassword = request.POST.get('confirmpassword')
        name = request.POST.get("name", "").strip()

         #Regex to ensure the name and las
        name_regex = r"^[A-Za-z]+(?: [A-Za-z'-]+)+$"
        if not name: 
            messages.error(request, "Full name is required.")
            return render(request, "TeacherRegistration.html")
        
        if not re.match(name_regex, name):
            messages.error(request, "Full name is Required")
            return render(request, "TeacherRegistration.html")
        if User.objects.filter(email=email).exists():
            print("Teacher Register: User already exists ---")
            return render(request, 'TeacherRegistration.html', {'error': 'Email already exists'})
        # Password authentication
        if password != confirmpassword:
            messages.error(request, "Password do not match.")
            return render(request, "TeacherRegistration.html")
        

        #Email authentication
        if User.objects.filter(email=email).exists(): 
            messages.error(request, "Email already exists.") 
            return render(request, "TeacherRegistration.html")
        

        if User.objects.filter(email=email).exists():
            print("Teacher Register: User already exists ---")
            return render(request, 'TeacherRegistration.html', {'error': 'Email already exists'})

        try:
            # Create User
            user = User.objects.create_user(
                username=request.POST.get('name'),  # Changed from email to name
                email=email, 
                password=password
            )

            # Create Profile - Student or Teacher

            teacher = Teacher.objects.create(
                user=user,
                full_name=request.POST.get('name'),
                license_number=request.POST.get('license'),
                specialization=request.POST.get('specialization'),
                profile_image_url=image_url
            )
            
            # Auto Login
            login(request, user)
            return redirect('signin_page_view') # replace with 'teacher_dashboard' when ready

        except Exception as e:
            print(f"--- CRITICAL ERROR DURING SAVE: {e} ---")
            return render(request, 'TeacherRegistration.html', {'error': str(e)})

    return render(request, 'TeacherRegistration.html')

"""Added By Mark: For redirects """

class CustomLoginView(LoginView):
    template_name = 'StudentHomePage.html'

    def get_success_url(self):
        user = self.request.user

        # this check for the student profile
        if hasattr(user, 'students_student_profile'):
            # The user has a student profile, redirect to their dashboard
            return reverse_lazy('student_home')
        
        #  this check for the teacher profile
        elif hasattr(user, 'teachers_teacher_profile'):
            # The user has a teacher profile, redirect them
            return reverse_lazy('teacher_home') 
        
        # Fallback for other users (like superusers without profiles)
        else:
            return reverse_lazy('SignInPage.html')

def signin_page_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # DEBUGGING PRINTS - Check your terminal/console!
            print(f"User {email} logged in.")
            print(f"Has Student Profile: {hasattr(user, 'students_student_profile')}")
            
            if user.is_student:
                return redirect('student_home')
            elif user.is_teacher:
                return redirect('teacher_home')
            else:
                print("User has no profile linked!")
                return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
            print(f"Authentication failed for {email}")

    return render(request, 'SignInPage.html')

def logout_view(request):
    logout(request)
    return redirect("home")

