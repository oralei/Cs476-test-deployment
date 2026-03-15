from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from courses.models import Course, Task, TaskSubmission, Notification
from courses.observers import SubmissionSubject, SubmissionObserver
from functools import wraps
import cloudinary.uploader  # For task submission

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

# Create your views here.

"""
Name Function: Home
type: Function
Purpose: It is used connect django with home html file through an http request
"""
def studentHome(request):
    user = request.user
    unread_notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')
    context = {
        'notifications': unread_notifications,
        'notification_count': unread_notifications.count()
    }
    return render(request, 'StudentHomePage/templates/StudentHomePage.html', context)

@login_required
@student_required
def markNotificationAsRead(request, notification_id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
    previous_page = request.META.get('HTTP_REFERER', '/')
    return redirect(previous_page)

"""
Name Function: Calendar
Added by: Ariel
type: Function
Purpose: It is used connect django with Calendar html file through an http request
"""
@login_required
@student_required
def Calendar(request):
    current_student = request.student_profile
    courses = current_student.enrolled_courses.all()
    tasks = Task.objects.filter(assigned_students=current_student)
    events_data = []

    for task in tasks:
        start_str = task.start_date.isoformat() if task.start_date else None
        end_str = task.due_date.isoformat() if task.due_date else None

        if not start_str and end_str:
            start_str = end_str

        if not start_str:
            continue

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
        'student': student
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
        if course.students.count() < course.max_students:
            course.students.add(student)
        return redirect('my-courses')
    return HttpResponseBadRequest("Invalid Request")

"""
Added by Mark: Student Course List Page
Notes: Shows all currently enrolled courses for the logged in student.
"""
@login_required
@student_required
def myCourses(request):
    student = request.student_profile
    courses = student.enrolled_courses.all()
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
        course = get_object_or_404(Course, id=course_id, students=student)
        course.students.remove(student)
        return redirect('my-courses')
    return HttpResponseBadRequest("Invalid Request")

""" -------------------------- Task Views/Functions ------------------------------ """

"""
Added by Mark: Tasks Page
Notes: Page that displays all the tasks a student has.
"""
@login_required
@student_required
def studentTasks(request):
    student = request.student_profile
    tasks = Task.objects.filter(assigned_students=student).order_by('due_date')
    task_data = []
    for t in tasks:
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
Notes: Page for adding a submission for a specific task.
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
        uploaded_file_url = submission.file_url if submission else ""

        if media_file:
            try:
                upload_result = cloudinary.uploader.upload(
                    media_file,
                    folder="submission_files",
                    resource_type="auto"
                )
                uploaded_file_url = upload_result.get('secure_url')
                print(f"Task Submit: Cloudinary Success: {uploaded_file_url}")
            except Exception as e:
                print(f"Task Submit: Cloudinary Error: {e}")

        if submission:
            submission.submission_text = submission_text
            if uploaded_file_url:
                submission.file_url = uploaded_file_url
            submission.save()
        else:
            submission = TaskSubmission.objects.create(
                task=task,
                student=student,
                submission_text=submission_text,
                file_url=uploaded_file_url,
                status='pending'
            )

        # Observer Pattern Implementation
        subject = SubmissionSubject(submission)
        teacher_observer = SubmissionObserver()
        subject.attach(teacher_observer)
        subject.set_state('pending')

        return redirect('student-tasks')

    context = {
        'task': task,
        'submission': submission
    }
    return render(request, 'tasks/templates/student-task-submit.html', context)