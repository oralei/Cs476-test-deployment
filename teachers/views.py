from django.shortcuts import render
#from django.contrib.auth.decorators import login_required

# Create your views here.

#@login_required


"""
Name Function: Home
type: Function 
Purpose: Connects to the Teacher Home dashboard
"""
def teacherHome(request):  
    # Looks in teachers/features/Home/templates/Home/Home.html
    return render(request, 'TeacherHomePage/templates/TeacherHomePage.html')

"""
Name Function: Calendar
type: Function 
Purpose: Connects to the Teacher Calendar feature
"""
def Calendar(request):  
    # Looks in teachers/features/Calendar/templates/Calendar/Calendar.html
    return render(request, 'Calendar/Calendar.html')

"""
Name Function: My_Student
type: Function 
Purpose: Connects to the My Student management feature
"""
def My_Student(request):  
    # Looks in teachers/features/My_Student/templates/My_Student/My_Student.html
    return render(request, 'My_Student/templates/My_Student.html')

"""
Name Function: Create_Task
type: Function 
Purpose: Connects to the Task creation feature
"""
def Create_Task(request):  
    # Looks in teachers/features/Create_Task/templates/Create_Task/Create_Task.html
    return render(request, 'Create_Task/Create_Task.html')

"""
Name Function: Meeting
type: Function 
Purpose: Connects to the Meeting/Video call feature
"""
def Meeting(request):  
    # Looks in teachers/features/Meeting/templates/Meeting/Meeting.html
    return render(request, 'Meeting/Meeting.html')