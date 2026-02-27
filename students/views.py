from django.shortcuts import render

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
Name Function: Tasks
type: Function 
Purpose:It is used connect django with Calender Tasks file through an http request

"""
def Courses(request):  
    return render(request, 'Courses/templates/Courses.html')