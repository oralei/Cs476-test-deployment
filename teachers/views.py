from django.shortcuts import render, redirect, get_object_or_404
from courses.models import Course, Task, TaskSubmission, TaskFeedback
from teachers.models import Teacher # Import the Teacher model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps
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
def teacherHome(request):  
    # Looks in teachers/features/Home/templates/Home/Home.html
    return render(request, 'TeacherHomePage/templates/TeacherHomePage.html')


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
    
    # Grab all courses created by the specific teacher
    courses = Course.objects.filter(teacher=current_teacher)

    # Pass those courses to the HTML template in a context dictionary
    context = {
        'courses': courses
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

        # Save the course to MongoDB
        Course.objects.create(
            title=course_title,
            description=course_description,
            max_students=max_students,
            teacher=current_teacher
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

    # Get the specific course by ID. 
    # Security: We also pass teacher=current_teacher to ensure they can't view another teacher's course!
    course = get_object_or_404(Course, id=course_id, teacher=current_teacher)

    # 2. Pass the single course to the HTML template
    context = {
        'course': course
    }
    return render(request, 'teacher-courses/templates/teacher-course-main.html', context)

"""
Name Function: Calendar
type: Function 
Purpose: Connects to the Teacher Calendar feature
"""
def Calendar(request):  
    # Looks in teachers/features/Calendar/templates/Calendar/Calendar.html
    return render(request, 'Calendar/templates/teacherCalendar.html')


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
Added by Mark: View All Submissions Page
Notes: A page for seeing all the submissions attached to a specific task. Can lead to a Give Feedback Page
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
        
        # Mark the submission as reviewed!
        submission.status = 'reviewed'
        submission.save()

        # Redirect back to the list of submissions for this task
        return redirect('teacher-task-submissions', task_id=submission.task.id)

    context = {
        'submission': submission,
        'feedback': feedback
    }
    return render(request, 'tasks/templates/teacher-feedback.html', context)