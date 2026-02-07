from django.shortcuts import render, redirect
import cloudinary
import cloudinary.uploader
from django.contrib import messages
from .models import Student, Teacher
# Create your views here.
"""
Author: Saim Munshi
Name Function: register_view
type: Function 
Purpose: direct view.py django to the correct html file
"""


def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        
        # ... (Cloudinary upload logic here) ...

        image_file = request.FILES.get('UploadPFP')
        image_url = ""

        if image_file:
            print(f"Found file: {image_file.name}") # Alarm 2
            try:
                # Force the upload and catch any error
                upload_result = cloudinary.uploader.upload(
                    image_file, 
                    folder="Mentora_Profiles"
                )
                image_url = upload_result.get('secure_url')
                print(f"SUCCESS! Cloudinary URL: {image_url}") # Alarm 3
            except Exception as e:
                print(f"CLOUDINARY ERROR: {e}") # This tells us WHY no folder was made
        else:
            print("No file was found in request.FILES!")
        image_url = None 
        role = request.POST.get('role')
        image_file = request.FILES.get('UploadPFP') #
        if role == 'student':
            # Create a document in the Students collection
            Student.objects.create(
                full_name=request.POST.get('name'),
                email=request.POST.get('email'),
                student_id=request.POST.get('studentId'),
                profile_image_url=image_url
            )
        elif role == 'teacher':
            # Create a document in the Teachers collection
            Teacher.objects.create(
                full_name=request.POST.get('name'),
                email=request.POST.get('email'),
                license_number=request.POST.get('license'),
                specialization=request.POST.get('specialization'),
                profile_image_url=image_url
            )
        return redirect('login')
    return render(request, 'registration.html')