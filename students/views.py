from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from courses.models import Course, Task, TaskSubmission, Notification, TaskFeedback
from courses.observers import SubmissionSubject, SubmissionObserver
from functools import wraps
import cloudinary.uploader  # For task submission
from django.db.models import Q  # For "or" queries
from django.contrib import messages  # For error messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
# Create your views here.
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
Name Function: Home
type: Function 
Purpose:It is used connect django with home html file through an http request
"""
@login_required
@student_required
def studentHome(request):  
    user = request.user 
    student_profile = request.student_profile # Provided by your decorator
    
  
    # Added Saim Munshi: Count of courses the student is enrolled in
    course_count = student_profile.enrolled_courses.count()
    
   
    # Added Saim Munshi: Task model has assigned_students many to many relationship
    task_count = Task.objects.filter(assigned_students=student_profile).count()

    #Added By Saim Munshi: Mentor Count For student
    mentor_count = Course.objects.filter(students=student_profile).values('teacher').distinct().count()

    #Added By Saim Munshi: upcoming task same logic from mentors task wedget
    upcoming_tasks = Task.objects.filter( assigned_students=student_profile).order_by('due_date')[:5]

    # Notifications logic (kept from your original code)
    unread_notifications = Notification.objects.filter(
        user=user, 
        is_read=False
    ).order_by('-created_at')
    
    context = {
        'student': student_profile,
        'course_count': course_count,
        'task_count': task_count,
        'mentor_count': mentor_count,
        'upcoming_tasks': upcoming_tasks,
        'notifications': unread_notifications,
        'notification_count': unread_notifications.count()
    }
    
    return render(request, 'StudentHomePage/templates/StudentHomePage.html', context)
@login_required
@student_required
def markNotificationAsRead(request, notification_id):
    if request.method == "POST":
        # 1. Fetch the notification (ensure it actually belongs to the logged-in user for security!)
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        
        # 2. Change the status to read
        notification.is_read = True
        notification.save()
        
    # 3. Redirect the user right back to the page they were just on
    # HTTP_REFERER gets the URL of the page the user clicked the button from
    previous_page = request.META.get('HTTP_REFERER', '/') 
    return redirect(previous_page)

"""
Name Function: Calender
Added by: Ariel
type: Function 
Purpose:It is used connect django with Calender html file through an http request
"""
@login_required
@student_required
def Calendar(request):  
    current_student = request.student_profile
    # Get courses this specific student is enrolled in
    courses = current_student.enrolled_courses.all()

    # Get tasks assigned to this student
    tasks = Task.objects.filter(assigned_students=current_student)
    events_data = []
    
    for task in tasks:
        start_str = task.start_date.isoformat() if task.start_date else None
        end_str = task.due_date.isoformat() if task.due_date else None

        # If the task doesn't have a start date, use the due date so the event still appears on the calendar.
        if not start_str and end_str:
            start_str = end_str
            
        if not start_str:
            continue # Skip tasks without dates
            
        events_data.append({
            'id': str(task.id),
            'title': task.title,
            'start': start_str,
            'end': end_str,
            'extendedProps': {
                'type': 'assignment',
                'course': str(task.course_id),
            }
        })

    context = {
        'courses': courses,
        'events_data': events_data,
    }
    
    return render(request, 'Calendar/templates/Calendar.html', context)

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
Modified: Added search functionality for teacher_code / course_code and hides private courses by default.
"""
@login_required
@student_required
def courseBrowser(request):
    student = request.student_profile

    if request.method == "POST":
        # Get the code from the search form input
        search_code = request.POST.get('course_code', '').strip()
        
        if search_code:
            # Search for courses matching EITHER the course_code OR the teacher's teacher_code
            # This intentionally bypasses the 'private=False' check to allow finding private courses via code
            courses = Course.objects.filter(
                Q(course_code=search_code) | Q(teacher__teacher_code=search_code)
            )
            
            # If no courses are found, send an error message to display in the HTML
            if not courses.exists():
                messages.error(request, "No courses found with that code.")
        else:
            # Fallback if they somehow submit an empty POST
            courses = Course.objects.filter(private=False)
    else:
        # Standard GET request: Only show non-private courses
        courses = Course.objects.filter(private=False)

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
            submission = TaskSubmission.objects.create(
                task=task,
                student=student,
                submission_text=submission_text,
                file_url=uploaded_file_url,  # Save the secure_url string!
                status='pending'
            )
            
        # Observer Pattern Implementation
        # -------------------------------------------------------------------
        subject = SubmissionSubject(submission)
        teacher_observer = SubmissionObserver() # Create observer
        subject.attach(teacher_observer)     # Attach
        subject.set_state('pending')         # Changes state and notifies
            
        # Observer Pattern Implementation
        # -------------------------------------------------------------------
        subject = SubmissionSubject(submission)
        teacher_observer = SubmissionObserver() # Create observer
        subject.attach(teacher_observer)     # Attach
        subject.set_state('pending')         # Changes state and notifies
        
        return redirect('student-tasks')

    # Note from Mark: Context to be sent to page for Task data retrieval. If there's already a submission, retrieve 
    # that data as well. It will be used in the above if condition for editing a submission or making a new one.
    context = {
        'task': task,
        'submission': submission
    }
    
    return render(request, 'tasks/templates/student-task-submit.html', context)

@login_required
def student_feedback(request):

    # Added by Matthew/Spooky: Retrieve all feedback where the current user is the receiver.
    feedback_list = TaskFeedback.objects.filter(submission__student__user=request.user).order_by("-graded_at")
    # Added by Matthew/Spooky: Count unread feedback items.
    unread_count = feedback_list.filter(is_read=False).count()

    # Added by Matthew/Spooky: Render the student feedback page with feedback data.
    return render(request, "tasks/templates/student-feedback.html", {
        "feedback_list": feedback_list,
        "unread_count": unread_count
    })


@login_required
@require_POST
def mark_feedback_read(request, feedback_id):

    # Added by Matthew/Spooky: Retrieve the feedback ensuring the logged in user is the receiver.
    feedback = get_object_or_404(TaskFeedback, id=feedback_id, submission__student__user=request.user)

    # Added by Matthew/Spooky: Mark feedback as read.
    feedback.is_read = True

    # Added by Matthew/Spooky: Save changes to the database.
    feedback.save()

    # Added by Matthew/Spooky: Return JSON response showing success.
    return JsonResponse({"success": True, "feedback_id": str(feedback.id)})


@login_required
@require_POST
def archive_feedback(request, feedback_id):

    # Added by Matthew/Spooky: Retrieve feedback ensuring the logged in student owns it.
    feedback = get_object_or_404(TaskFeedback, id=feedback_id, submission__student__user=request.user)

    # Added by Matthew/Spooky: Mark feedback as archived for the receiver.
    feedback.is_archived_for_receiver = True

    # Added by Matthew/Spooky: Mark feedback as read.
    feedback.is_read = True

    # Added by Matthew/Spooky: Save changes to the database.
    feedback.save()

    # Added by Matthew/Spooky: Return JSON response showing success.
    return JsonResponse({"success": True, "feedback_id": str(feedback.id)})