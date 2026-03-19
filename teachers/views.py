from django.shortcuts import render, redirect, get_object_or_404
from courses.models import Course, Task, TaskSubmission, TaskFeedback
from teachers.models import Teacher # Import the Teacher model
from django.contrib.auth.decorators import login_required
from courses.observers import SubmissionSubject, FeedbackObserver
from courses.models import Notification
from django.http import HttpResponseForbidden
from functools import wraps
from datetime import date
from django.db.models import Count

#from django.contrib.auth.decorators import login_required

# Create your views here.

# Added by Mark: Helper function to check teacher profile. 
# It checks both if the user accessing is a user of type teacher 
# This is reused throughout most if not all the views.
def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_teacher:
            return HttpResponseForbidden("You must be logged in as a teacher.")
        request.teacher_profile = request.user.teachers_teacher_profile 
        return view_func(request, *args, **kwargs)
    return wrapper

"""
Name Function: Home
type: Function 
Purpose: Connects to the Teacher Home dashboard
"""
@login_required
@teacher_required
def teacherHome(request):  
    user = request.user 
    teacher = request.teacher_profile
    print(f"Logged in User Email: {user.email} - Teacher Profile Name: {repr(teacher.full_name)}")
    
    # Fetch user's unread notifications from the database
    unread_notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')

    #Added By Saim Munshi:Fetch 5upcoming task from database based on today data and ordered by due date

    upcoming_tasks = Task.objects.filter( course__teacher = teacher,due_date__gte= date.today()).order_by("due_date")[:5]

    # Added By Saim Munshi: Count of all courses created by this teacher
    course_count = Course.objects.filter(teacher=teacher).count()

    # Added By Saim Munshi: First count of all unique students enrolled across all this teacher's courses than we filter students where their enrolled_courses has this teacher
    student_count = Course.objects.filter(teacher=teacher).aggregate(total=Count('students', distinct=True))['total'] or 0

    # Added By Saim Munshi: Count of all tasks created across all this teacher's courses 

    task_count = Task.objects.filter(course__teacher=teacher).count()
    context = {
       'teacher': teacher,
        'notifications': unread_notifications,
        'notification_count': unread_notifications.count(),
        'upcoming_tasks': upcoming_tasks,
        'course_count': course_count,
        'student_count': student_count,
        'task_count': task_count,
    }
   
    return render(request, 'TeacherHomePage/templates/TeacherHomePage.html', context)

@login_required
@teacher_required
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


""" -------------------------- Course Views/Functions ------------------------------"""
"""
Added by Mark: Course List page
Notes: Queries the database to obtain all courses under the logged in teacher.
       It passes the queried Courses as an object called "context" to the rendered page.
"""
@login_required
@teacher_required
def teacherCourseList(request):  
    current_teacher = request.teacher_profile
    # Fetch user's unread notifications from the database (same as dashboard)
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    # Grab all courses created by the specific teacher
    courses = Course.objects.filter(teacher=current_teacher)

    # Pass those courses to the HTML template in a context dictionary
    context = {
        'courses': courses,
        'notifications': unread_notifications
    }
    return render(request, 'teacher-courses/templates/teacher-course-list.html', context)


"""
Added by Mark: Create Course
Notes: Uses form fields from create-course.html to create a new Course object in MongoDB.
       You likely won't need to change anything here if working on front-end.
"""
@login_required
@teacher_required
def teacherCreateCourse(request):  
    current_teacher = request.teacher_profile
    
    # Handle the form submission
    if request.method == "POST":
        course_title = request.POST.get('title')
        course_description = request.POST.get('description')
        max_students = request.POST.get('max_students')

        is_private = request.POST.get('private-box') == 'on'

        # Save the course to MongoDB
        Course.objects.create(
            title=course_title,
            description=course_description,
            max_students=max_students,
            teacher=current_teacher,
            private=is_private
        )
        # Added By Saim Munshi: Create Course Notification:
        Notification.objects.create(
            user=request.user,
            notification_type=f"Create Course",
            message=f"Course '{course_title}' has been successfully created!"
        )
        
        # Redirect back to the course list
        return redirect('teacher-course-list')

    # If it's just a GET request, render the empty form
    return render(request, 'teacher-courses/templates/create-course.html')

"""
Added by Mark: Course Main Page
Notes: This view is for obtaining a specific Course object under the current logged in teacher.
       It passes the queried Courses as an object called "context" to the rendered page.
"""
@login_required
@teacher_required
def teacherCourseMain(request, course_id):
    current_teacher = request.teacher_profile
    # Fetch user's unread notifications from the database (same as dashboard)
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    # Get the specific course by ID. 
    # Security: We also pass teacher=current_teacher to ensure they can't view another teacher's course!
    course = get_object_or_404(Course, id=course_id, teacher=current_teacher)

    # 2. Pass the single course to the HTML template
    context = {
        'course': course,
        'notifications': unread_notifications
    }
    return render(request, 'teacher-courses/templates/teacher-course-main.html', context)

"""
Name Function: Calendar
Added by Ariel:
type: Function 
Purpose: Connects to the Teacher Calendar feature
"""
@login_required
@teacher_required
def Calendar(request):  
    current_teacher = request.teacher_profile

    # Get courses for this teacher
    courses = Course.objects.filter(teacher=current_teacher)
    course_students_map = {}
    for c in courses:
        course_students_map[str(c.id)] =[
            {'id': str(s.id), 'name': s.full_name} for s in c.students.all()
        ]

    tasks = Task.objects.filter(course__teacher=current_teacher)
    events_data = []
    
    for task in tasks:
        events_data.append({
            'id': str(task.id),
            'title': task.title,
            # FullCalendar expects YYYY-MM-DD strings for dates
            'start': task.start_date.isoformat() if task.start_date else None,
            'end': task.due_date.isoformat() if task.due_date else None,
            'extendedProps': {
                'type': 'assignment',
                'course': str(task.course.id),
                # Task can have multiple students, so we need to get ids
                'students': [str(student.id) for student in task.assigned_students.all()]
            }
        })

    context = {
        'courses': courses,
        'course_students_map': course_students_map,
        'events_data': events_data,
    }
    return render(request, 'Calendar/templates/teacherCalendar.html', context)


def My_Student(request):  
    # Looks in teachers/features/My_Student/templates/My_Student/My_Student.html
    return render(request, 'My_Student/templates/My_Student.html')


def Meeting(request):  
    # Looks in teachers/features/Meeting/templates/Meeting/Meeting.html
    return render(request, 'Meeting/templates/Meeting.html')

""" -------------------------- Task Views/Functions ------------------------------"""

"""
Added by Mark: Create Task
Notes: This view uses the data from the POST form in create-task.html to create a Task object.
       To note, a single task can be given to multiple students at once which is why it uses a list of student ids.
"""
@login_required
@teacher_required
def Create_Task(request):  
    current_teacher = request.teacher_profile

    if request.method == "POST":
        course_id = request.POST.get('course')
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date') or None 
        due_date = request.POST.get('due_date') or None
        student_ids = request.POST.getlist('students') 

        course = get_object_or_404(Course, id=course_id, teacher=current_teacher)

        new_task = Task.objects.create(
            course=course,
            title=title,
            description=description,
            start_date=start_date,
            due_date=due_date
        )
        # Added By Saim Munshi: Create Tasks Notification:
        Notification.objects.create(
            user=request.user,
            notification_type=f"Create Task",
            message=f"Task '{title}' has been successfully created!"
        )
        if student_ids:
            new_task.assigned_students.set(student_ids)

        return redirect('teacher_home')

    courses = Course.objects.filter(teacher=current_teacher)
    
    course_students_map = {}
    for c in courses:
        course_students_map[str(c.id)] = [
            {'id': str(s.id), 'name': s.full_name} for s in c.students.all()
        ]

    context = {
        'courses': courses,
        # 2. Just pass the normal python dictionary!
        'course_students_map': course_students_map 
    }
    return render(request, 'tasks/templates/create-task.html', context)

"""
Added by Mark: View task Submissions Page
Notes: A page for seeing the submissions attached to a specific task. Can lead to a Give Feedback Page
"""
@login_required
@teacher_required
def teacherNeedsFeedbackList(request):
    current_teacher = request.teacher_profile
    
    # Iteration 2: Instead, we get all courses so we can show or filter courses in the future
    # Get all courses taught by the current teacher
    courses = Course.objects.filter(teacher=current_teacher)
    
    # Build a list that pairs each course with its pending submissions
    course_data = []
    for course in courses:
        # Get pending submissions strictly for this specific course
        pending_subs = TaskSubmission.objects.filter(
            task__course=course,
            status='pending'
        ).order_by('submitted_at')
        
        # Append the course and its submissions to our list
        course_data.append({
            'course': course,
            'submissions': pending_subs
        })
        
    context = {
        'course_data': course_data
    }
    return render(request, 'tasks/templates/needs-feedback-list.html', context)

"""
Added by Mark: View task Submissions Page
Notes: A page for seeing the submissions attached to a specific task. Can lead to a Give Feedback Page
"""
@login_required
@teacher_required
def teacherTaskSubmissions(request, task_id):
    current_teacher = request.teacher_profile

    # Get the task, ensure it belongs to this teacher
    task = get_object_or_404(Task, id=task_id, course__teacher=current_teacher)
    
    # Get all assigned students and attach their submission if it exists
    student_data = []
    for student in task.assigned_students.all():
        submission = TaskSubmission.objects.filter(task=task, student=student).first()
        student_data.append({
            'student': student,
            'submission': submission,
        })

    context = {
        'task': task,
        'student_data': student_data
    }
    return render(request, 'tasks/templates/teacher-task-submissions.html', context)

"""
Added by Mark: Give Feedback Page
Notes: A page for giving feedback on a specific task.
"""
@login_required
@teacher_required
def teacherFeedback(request, submission_id):
    current_teacher = request.teacher_profile

    # Get the specific submission
    submission = get_object_or_404(TaskSubmission, id=submission_id, task__course__teacher=current_teacher)
    
    # Get existing feedback if the teacher is editing a previous grade
    feedback = TaskFeedback.objects.filter(submission=submission).first()

    if request.method == "POST":
        grade = request.POST.get('grade')
        comments = request.POST.get('comments', '')

        if feedback:
            # Update existing feedback
            feedback.grade = grade
            feedback.comments = comments
            feedback.save()
        else:
            # Create new feedback
            TaskFeedback.objects.create(
                submission=submission,
                grade=grade,
                comments=comments
            )
        
        # Observer Pattern
        subject = SubmissionSubject(submission)
        student_observer = FeedbackObserver() # Create observer
        subject.attach(student_observer)     # Attach
        subject.set_state('reviewed')        # Changes state and notifies
        # ==========================================

        # Redirect back to the list of submissions for this task
        return redirect('teacher-task-submissions', task_id=submission.task.id)

    context = {
        'submission': submission,
        'feedback': feedback
    }
    return render(request, 'tasks/templates/teacher-feedback.html', context)



#Added By Saim: Edit course take edit course using create course form an
@login_required
@teacher_required
def editCourse(request, course_id):
    #Added By Saim Munshi: get course by course id
    course = Course.objects.get(id=course_id)
     #Added By Saim Munshi: request post retreieve and save course title and description save
    if request.method == "POST":
        course.title = request.POST.get("title")
        course.description = request.POST.get("description")
        course.private = request.POST.get('private-box') == 'on'
        course.save()
         # Added By Saim Munshi: Create Edit Notification:
        Notification.objects.create(
            user=request.user,
            notification_type=f"Edit Course",
            message=f"Course '{course.title}' has been successfully edited!" # (Changed "created" to "edited"  for accuracy)
        )
        #Added By Saim Munshi: if not redirect to teacher course list page
        return redirect("teacher-course-list")
    #Added By Saim Munshi: course context dictonary 
    context = {
        "course": course
    }

    return render(request, "teacher-courses/templates/create-course.html", context)

# Added By Saim Munshi: Delete course logic
@login_required
@teacher_required
def deleteCourse(request, course_id):
    # Retrieve the course specifically for the logged-in teacher
    course = get_object_or_404(Course, id=course_id, teacher=request.teacher_profile)
    
    if request.method == "POST":
        course.delete()
         # Added By Saim Munshi: Create Delete Notification:
        Notification.objects.create(
            user=request.user,
            notification_type=f"Delete Course",
            message=f"Course '{course.title}' has been successfully Deleted!"
        )
        # Redirect back to the course list page
        return redirect('teacher-course-list')
    
    return redirect('teacher-course-list')

# Added By Saim Munshi: Edit task  using create task form 
@login_required
@teacher_required
def editTask(request, task_id): 
    task = get_object_or_404(Task, id=task_id)
    # Filter courses to only those owned by this teacher
    courses = Course.objects.filter(teacher=request.teacher_profile) 
    students = []
    if request.method == "POST":
        task.title = request.POST.get("title")
        task.description = request.POST.get("description") 
        task.start_date = request.POST.get("start_date") 
        task.due_date = request.POST.get("due_date") 
        
        course_id = request.POST.get("course")
        if course_id:
            course = get_object_or_404(Course, id=course_id, teacher=request.teacher_profile)
            task.course = course
        
        task.save()
        
        student_ids = request.POST.getlist('students')
        task.assigned_students.set(student_ids) 
        
        Notification.objects.create(
            user=request.user,
            notification_type="Edit task",
            message=f"Task '{task.title}' has been successfully updated!"
        )
        return redirect("teacher-course-main", course_id=task.course.id)

        if task.course:
            students = task.course.students.all()

    context = {
        "task": task,
        "courses": courses,
        "students": students,
    }

    return render(request, "tasks/templates/create-task.html", context)

# Added By Saim Munshi: Delete task logic
@login_required
@teacher_required
def deleteTask(request, task_id):
    # Retrieve the course specifically for the logged-in teacher
    task = get_object_or_404(Task, id=task_id, course__teacher=request.teacher_profile)
    course_id = str(task.course.id) 

    if request.method == "POST":
        task_title = task.title
        task.delete()
        
         # Added By Saim Munshi: Create Delete Notification:
        Notification.objects.create(
            user=request.user,
            notification_type=f"Delete Task",
            message=f"Task '{task_title}' has been successfully Deleted!"
        )
        # Added By Saim Munshi:redirect back to the course list page
        return redirect('teacher-course-main', course_id=course_id)
    
    return redirect('teacher-course-main', course_id=course_id)