from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from courses.models import Course

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
    return render(request, '\Home\templates\Calender.html')

"""
Name Function: Mentor
type: Function 
Purpose:It is used connect django with Calender Mentor file through an http request

"""
def Mentor(request):  
    return render(request, '\Mentors\templates\Mentor.html')


"""
Name Function: Skills
type: Function 
Purpose:It is used connect django with Calender Skills file through an http request

"""
def Progress(request):  
    return render(request, '\Progess\templates\Progess.html')


"""
Student Courses Views and Functions:
- Mark: Below are all the Course related functionality on the student's side
"""
# Helper function to check auth and get the student profile
def get_student_profile(user):
    if not getattr(user, 'is_student', False):
        return None
    try:
        # Assuming this is your related name based on previous examples
        return user.students_student_profile 
    except AttributeError:
        return None

@login_required
def courseBrowser(request):
    student = get_student_profile(request.user)
    if not student:
        return HttpResponseForbidden("You must be logged in as a student.")

    courses = Course.objects.all()
    context = {
        'courses': courses,
        'student': student  # Passing student so we can check if they already joined a course
    }
    # Note: Update template path if needed based on your folder structure
    return render(request, 'Courses/templates/course-browser.html', context)

@login_required
def joinCourse(request, course_id):
    student = get_student_profile(request.user)
    if not student:
        return HttpResponseForbidden("You must be logged in as a student.")

    if request.method == "POST":
        course = get_object_or_404(Course, id=course_id)
        
        # Check if course is not full
        if course.students.count() < course.max_students:
            course.students.add(student) # Adds the student to the ManyToMany field!
        
        return redirect('my-courses')
    
    return HttpResponseBadRequest("Invalid Request")

@login_required
def myCourses(request):
    student = get_student_profile(request.user)
    if not student:
        return HttpResponseForbidden("You must be logged in as a student.")

    # Only get courses where THIS student is in the 'students' ManyToMany list
    courses = student.enrolled_courses.all()
    
    context = {'courses': courses}
    return render(request, 'Courses/templates/my-courses.html', context)

@login_required
def studentCourseMain(request, course_id):
    student = get_student_profile(request.user)
    if not student:
        return HttpResponseForbidden("You must be logged in as a student.")

    # get_object_or_404 ensures the student is actually enrolled in this specific course!
    course = get_object_or_404(Course, id=course_id, students=student)
    
    context = {'course': course}
    return render(request, 'Courses/templates/student-course-main.html', context)

@login_required
def leaveCourse(request, course_id):
    student = get_student_profile(request.user)
    if not student:
        return HttpResponseForbidden("You must be logged in as a student.")

    if request.method == "POST":
        # get_object_or_404 with students=student ensures they can only leave a course they are actually in
        course = get_object_or_404(Course, id=course_id, students=student)
        
        # Remove the student from the ManyToMany list
        course.students.remove(student) 
        
        # Redirect back to their course list
        return redirect('my-courses')
    
    return HttpResponseBadRequest("Invalid Request")