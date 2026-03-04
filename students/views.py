from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from courses.models import Course, Task, TaskSubmission
from functools import wraps
import cloudinary.uploader  # For task submission

# Create your views here.

"""
Name Function: Home
type: Function 
Purpose:It is used connect django with home html file through an http request
"""
def studentHome(request):  
    return render(request, 'StudentHomePage/templates/StudentHomePage.html')

"""
Name Function: Calender
type: Function 
Purpose:It is used connect django with Calender html file through an http request
"""
def Calender(request):  
    return render(request, '/Home/templates/Calender.html')

def Mentor(request):  
    return render(request, '/Mentors/templates/Mentor.html')

def Progress(request):  
    return render(request, '/Progess/templates/Progess.html')

""" ------------------------------ Student Courses Views/Functions ------------------------------ """
# Note: Below are all the Course related functionality on the student's side.

# Added by Mark: Helper function to check the student profile. 
# This is reused throughout all the views by adding @student_required just like @login_required
def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_student:
            return HttpResponseForbidden("You must be logged in as a student.")
        request.student_profile = request.user.students_student_profile
        return view_func(request, *args, **kwargs)
    return wrapper

"""
Added by Mark: Course Browser Page
Notes: A page for seeing all available courses and allows a student to enroll into it.
"""
@login_required
@student_required
def courseBrowser(request):
    student = request.student_profile

    courses = Course.objects.all()
    context = {
        'courses': courses,
        'student': student  # Passing student so we can check if they already joined a course
    }
    return render(request, 'Courses/templates/course-browser.html', context)

"""
Added by Mark: A function to link the current student to the course they clicked enroll onto.
"""
@login_required
@student_required
def joinCourse(request, course_id):
    student = request.student_profile

    if request.method == "POST":
        course = get_object_or_404(Course, id=course_id)
        
        # Check if course is not full using simple if
        if course.students.count() < course.max_students:
            course.students.add(student) # Adds the student to the ManyToMany field in Course model (object)
        
        return redirect('my-courses')
    
    return HttpResponseBadRequest("Invalid Request")

"""
Added by Mark: Student Course List Page
Notes: Shows all currently enrolled courses for the logged in student. Can lead to a specific Course Main page.
"""
@login_required
@student_required
def myCourses(request):
    student = request.student_profile

    # Only get courses where Tthe current student is in the 'students' ManyToMany list
    courses = student.enrolled_courses.all() # Note: enrolled_courses is a related_name in the Courses model, see courses/models.py
    
    context = {'courses': courses}
    return render(request, 'Courses/templates/my-courses.html', context)

"""
Added by Mark: Course Page
Notes: Student mirror of a Course Details page. 
"""
@login_required
@student_required
def studentCourseMain(request, course_id):
    student = request.student_profile

    # "get_object_or_404" is a Django function that retrieves a single object from a database 
    # and if the object does not exist, raises an Http404 exception. 
    # It's used everytime we need to load a page using a specific id (course, task, ubmission, feedback)
    course = get_object_or_404(Course, id=course_id, students=student)
    
    context = {'course': course}
    return render(request, 'Courses/templates/student-course-main.html', context)

"""
Added by Mark: Function that removes currently logged in student from a specific course
"""
@login_required
@student_required
def leaveCourse(request, course_id):
    student = request.student_profile

    if request.method == "POST":
        # get_object_or_404 with students=student ensures they can only leave a course they are actually in
        course = get_object_or_404(Course, id=course_id, students=student)
        
        # Remove the student from the ManyToMany list
        course.students.remove(student) 
        
        # Redirect back to their course list
        return redirect('my-courses')
    
    return HttpResponseBadRequest("Invalid Request")

""" -------------------------- Task Views/Functions ------------------------------ """

"""
Added by Mark: Tasks Page
Notes: Page that displays all the tasks a student has. Can lead to Task Submission page.
"""
@login_required
@student_required
def studentTasks(request):
    student = request.student_profile

    # Get all tasks specifically assigned to this student
    tasks = Task.objects.filter(assigned_students=student).order_by('due_date')

    # Package the tasks with their submission status so the HTML can display "Pending" vs "Submitted"
    task_data = []
    for t in tasks:
        # Check if a submission already exists for this task + student combination
        submission = TaskSubmission.objects.filter(task=t, student=student).first()
        task_data.append({
            'task': t,
            'status': submission.status if submission else 'Not Submitted',
            'is_submitted': bool(submission)
        })

    context = {'task_data': task_data}
    return render(request, 'tasks/templates/student-tasks.html', context)

"""
Added by Mark: Task Submission Page
Notes: Page for adding a submission for a specific task. Uses a POST form to upload fields to the database.
"""
@login_required
@student_required
def studentTaskSubmit(request, task_id):
    student = request.student_profile

    task = get_object_or_404(Task, id=task_id, assigned_students=student)
    submission = TaskSubmission.objects.filter(task=task, student=student).first()

    if request.method == "POST":
        submission_text = request.POST.get('submission_text', '')
        media_file = request.FILES.get('attached_file')
        
        # Keep the existing URL unless they upload a new file
        uploaded_file_url = submission.file_url if submission else ""

        # Cloudinary Upload Logic (similar to register logic)
        if media_file:
            try:
                # resource_type="auto" is REQUIRED for Cloudinary to accept videos!
                upload_result = cloudinary.uploader.upload(
                    media_file, 
                    folder="submission_files",
                    resource_type="auto" 
                )
                uploaded_file_url = upload_result.get('secure_url')
                print(f"Task Submit: Cloudinary Success: {uploaded_file_url}")
            except Exception as e:
                print(f"Task Submit: Cloudinary Error: {e}")
                # Note from Mark: Could add a messages.error here to tell the user it failed

        if submission:
            # Update existing submission
            submission.submission_text = submission_text
            if uploaded_file_url: 
                submission.file_url = uploaded_file_url
            submission.save()
        else:
            # Create a brand new submission
            TaskSubmission.objects.create(
                task=task,
                student=student,
                submission_text=submission_text,
                file_url=uploaded_file_url,  # Save the secure_url string!
                status='pending'
            )
        
        return redirect('student-tasks')

    # Note from Mark: Context to be sent to page for Task data retrieval. If there's already a submission, retrieve 
    # that data as well. It will be used in the above if condition for editing a submission or making a new one.
    context = {
        'task': task,
        'submission': submission
    }
    return render(request, 'tasks/templates/student-task-submit.html', context)