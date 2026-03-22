from django.shortcuts import render, redirect, get_object_or_404
from courses.models import Course, Task, TaskSubmission, TaskFeedback
from teachers.models import Teacher # Import the Teacher model
from django.contrib.auth.decorators import login_required
from courses.observers import SubmissionSubject, FeedbackObserver
from courses.models import Notification
from courses.observers import SubmissionSubject, FeedbackObserver
from courses.models import Notification
from django.http import HttpResponseForbidden
from functools import wraps
from datetime import date
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone #added by win516

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
    teacher_profile = Teacher.objects.get(user=request.user)
    print(f"Logged in User Email: {user.email} - Teacher Profile Name: {repr(teacher.full_name)}")
    
    # Fetch user's unread notifications from the database
    unread_notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')

    #Added By Saim Munshi:Fetch 5upcoming task from database based on today data and ordered by due date

    upcoming_tasks = Task.objects.filter( course__teacher = teacher,due_date__gte= date.today()).order_by("due_date")[:5]

    # Added By Saim Munshi: Count of all courses created by this teacher
    course_count = Course.objects.filter(teacher=teacher).count()

    # Added By Saim Munshi: First count of all unique students enrolled across all this teacher's courses than we filter 
    # students where their enrolled_courses has this teacher
    # student_count = Course.objects.filter(teacher=teacher).aggregate(total=Count('students', distinct=True))['total'] or 0
    
    # Updated by Mark: Safely get distinct student count to avoid MongoDB $size missing array error
    distinct_students = set()
    for course in Course.objects.filter(teacher=teacher):
        # Add all student IDs from this course into the set (sets automatically prevent duplicates)
        distinct_students.update(course.students.values_list('id', flat=True))

    student_count = len(distinct_students)

    # Added By Saim Munshi: Count of all tasks created across all this teacher's courses 

    task_count = Task.objects.filter(course__teacher=teacher).count()
    context = {
       'teacher': teacher_profile,
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
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
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
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    courses = Course.objects.filter(teacher=current_teacher)
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
        # Added By Saim Munshi: Create Course Notification
        Notification.objects.create(
            user=request.user,
            notification_type=f"Create Course",
            message=f"Course '{course_title}' has been successfully created!"
        )
        return redirect('teacher-course-list')
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
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    course = get_object_or_404(Course, id=course_id, teacher=current_teacher)
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
    courses = Course.objects.filter(teacher=current_teacher)
    course_students_map = {}
    for c in courses:
        course_students_map[str(c.id)] = [
            {'id': str(s.id), 'name': s.full_name} for s in c.students.all()
        ]
    tasks = Task.objects.filter(course__teacher=current_teacher)
    events_data = []
    for task in tasks:
        events_data.append({
            'id': str(task.id),
            'title': task.title,
            'start': task.start_date.isoformat() if task.start_date else None,
            'end': task.due_date.isoformat() if task.due_date else None,
            'extendedProps': {
                'type': 'assignment',
                'course': str(task.course.id),
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
    return render(request, 'My_Student/templates/My_Student.html')


def Meeting(request):
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
        # Added By Saim Munshi: Create Tasks Notification
        Notification.objects.create(
            user=request.user,
            notification_type=f"create_task",
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
    task = get_object_or_404(Task, id=task_id, course__teacher=current_teacher)
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
    submission = get_object_or_404(TaskSubmission, id=submission_id, task__course__teacher=current_teacher)
    feedback = TaskFeedback.objects.filter(submission=submission).first()
    if request.method == "POST":
        grade = request.POST.get('grade')
        comments = request.POST.get('comments', '')
        attachment_url = feedback.attachment_url if feedback else None
        file = request.FILES.get("attachment")
        # Added by Matthew/Spooky: If a file exists upload it to Cloudinary.
        if file:
            try:
                upload = cloudinary.uploader.upload(file, folder="Mentora_Feedback")
                attachment_url = upload.get("secure_url")
            except Exception as e:
                # Added by Matthew/Spooky: Print upload error to server console.
                print(f"Cloudinary Upload Error: {e}")

        if feedback:
            feedback.grade = grade
            feedback.comments = comments
            if file: # Only overwrite if a new file is uploaded
                feedback.attachment_url = attachment_url
            feedback.save()
        else:
            TaskFeedback.objects.create(
                submission=submission,
                grade=grade,
                comments=comments, 
                attachment_url=attachment_url
            )
        # Observer Pattern
        subject = SubmissionSubject(submission)
        student_observer = FeedbackObserver()
        subject.attach(student_observer)
        subject.set_state('reviewed')
        return redirect('teacher-task-submissions', task_id=submission.task.id)
    context = {
        'submission': submission,
        'feedback': feedback
    }
    return render(request, 'tasks/templates/teacher-feedback.html', context)


# Added By Saim: Edit course
@login_required
@teacher_required
def editCourse(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == "POST":
        course.title = request.POST.get("title")
        course.description = request.POST.get("description")
        course.private = request.POST.get('private-box') == 'on'
        course.save()
        Notification.objects.create(
            user=request.user,
            notification_type=f"Edit Course",
            message=f"Course '{course.title}' has been successfully edited!" # (Changed "created" to "edited"  for accuracy)
        )
        return redirect("teacher-course-list")
    context = {"course": course}
    return render(request, "teacher-courses/templates/create-course.html", context)

# Added By Saim Munshi: Delete course logic
@login_required
@teacher_required
def deleteCourse(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.teacher_profile)
    if request.method == "POST":
    # Added By Saim Munshi: gets all course title
        course_title = course.title
        # Added By Saim Munshi: gets all student enrolled in course
        enrolled_students = list(course.students.all())
        course.delete()

    
      
        # Added By Saim Munshi: Create Delete Notification for students
        for student in enrolled_students:
            Notification.objects.create(
                user=student.user,
                notification_type="course_deleted",
                message=f"The course '{course_title}' has been deleted."
            )
         # Added By Saim Munshi: Create Delete Notification for mentor:
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
        
        sstudent_ids = request.POST.getlist('students')
        task.assigned_students.set(sstudent_ids) 
        
        # Added By Saim Munshi: get student as list 
        student_ids = request.POST.getlist('students')
        task.assigned_students.set(student_ids) 
        
        # Added By Saim Munshi: Notify students
        for student in task.assigned_students.all():
            Notification.objects.create(
                user=student.user,
                notification_type="Edit task",
                message=f"The task '{task.title}' has been updated. Please check for changes."
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
        assigned_students = list(task.assigned_students.all())
        task.delete()

   
        # Added By Saim Munshi: Notify every student from the list we saved in memory
        for student in assigned_students:
            Notification.objects.create(
                user=student.user,
                notification_type="task_deleted",
                message=f"The task '{task_title}' has been deleted by the instructor."
            )


         # Added By Saim Munshi: Create Delete Notification:
        Notification.objects.create(
            user=request.user,
            notification_type=f"Delete Task",
            message=f"Task '{task_title}' has been successfully Deleted!"
        )
        # Added By Saim Munshi:redirect back to the course list page
        return redirect('teacher-course-main', course_id=course_id)
    
    return redirect('teacher-course-main', course_id=course_id)

""" -------------------------- Progress Views/Functions ------------------------------ """

# added by win516
@login_required
@teacher_required
def Progress(request):
    from django.utils import timezone
    current_teacher = request.teacher_profile
    courses = Course.objects.filter(teacher=current_teacher)

    student_map = {}
    course_names = []

    for course in courses:
        if course.title:
            course_names.append(course.title)

        for student in course.students.all():
            sid = str(student.id)

            total_tasks = Task.objects.filter(
                course=course,
                assigned_students=student
            ).count()

            completed_tasks = TaskSubmission.objects.filter(
                task__course=course,
                student=student,
                status='reviewed'
            ).count()

            pending_tasks = TaskSubmission.objects.filter(
                task__course=course,
                student=student,
                status='pending'
            ).count()

            # Overdue = past due date and not reviewed
            overdue = Task.objects.filter(
                course=course,
                assigned_students=student,
                due_date__lt=timezone.now()
            ).exclude(
                id__in=TaskSubmission.objects.filter(
                    student=student,
                    status='reviewed'
                ).values_list('task_id', flat=True)
            ).count()

            progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

            # Get specific overdue task names
            overdue_task_objects = Task.objects.filter(
                course=course,
                assigned_students=student,
                due_date__lt=timezone.now()
            ).exclude(
                id__in=TaskSubmission.objects.filter(
                    student=student,
                    status='reviewed'
                ).values_list('task_id', flat=True)
            )

            # Get specific pending task names
            pending_task_objects = TaskSubmission.objects.filter(
                task__course=course,
                student=student,
                status='pending'
            )

            if sid not in student_map:
                student_map[sid] = {
                    "name": student.full_name or "Unknown",
                    "courses": [],
                    "total_completed": 0,
                    "total_pending": 0,
                    "total_overdue": 0,
                    "total_tasks": 0,
                    "overdue_task_names": [],
                    "pending_task_names": [],
                }

            for t in overdue_task_objects:
                student_map[sid]["overdue_task_names"].append(
                    f"{t.title} ({course.title})"
                )

            for t in pending_task_objects:
                student_map[sid]["pending_task_names"].append(
                    f"{t.task.title} ({course.title})"
                )

            student_map[sid]["courses"].append({
                "course": course.title or "Untitled",
                "progress": progress,
                "completed": completed_tasks,
                "pending": pending_tasks,
                "overdue": overdue,
            })
            student_map[sid]["total_completed"] += completed_tasks
            student_map[sid]["total_pending"] += pending_tasks
            student_map[sid]["total_overdue"] += overdue
            student_map[sid]["total_tasks"] += total_tasks

    student_data = []
    for sid, s in student_map.items():
        total = s["total_tasks"]
        progress = int((s["total_completed"] / total) * 100) if total > 0 else 0
        status = 'behind' if progress < 40 or s["total_overdue"] > 0 else 'ontrack'

        student_data.append({
            "name": s["name"],
            "courses": s["courses"],
            "progress": progress,
            "completed": s["total_completed"],
            "pending": s["total_pending"],
            "overdue": s["total_overdue"],
            "status": status,
            "overdue_task_names": s["overdue_task_names"],
            "pending_task_names": s["pending_task_names"],
        })

    # Sort by progress ascending — lowest first
    student_data.sort(key=lambda x: x["progress"])

    needs_attention = sum(1 for s in student_data if s['status'] == 'behind')

    stats = {
        "active_students": len(student_data),
        "needs_attention": needs_attention,
        "avg_completion": int(sum(s["progress"] for s in student_data) / len(student_data)) if student_data else 0,
    }

    return render(request, "Progress/templates/Progress.html", {
        "students": student_data,
        "courses": course_names,
        "stats": stats,
    })
    

# Added by Stephen:
@login_required
@teacher_required
def teacherSettings(request):
    teacher = request.teacher_profile
    user = request.user

    if request.method == "POST":

        # Basic info
        # Basic info
        user.email = request.POST.get("email")
        teacher.full_name = request.POST.get("full_name")
        user.save()
        teacher.save()

        # Password fields
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password or confirm_password:

            if not current_password:
                messages.error(request, "Enter current password to change password")

            elif not user.check_password(current_password):
                messages.error(request, "Current password is incorrect")

            elif new_password != confirm_password:
                messages.error(request, "Passwords do not match")

            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully")

        else:
            messages.success(request, "Settings updated successfully")

        return redirect("teacher-settings")

    return render(request, "Setting/templates/teacher-settings.html", {"user": user})