from django.shortcuts import render

# Create your views here.
"""
Name Function: Home
type: Function 
Purpose:It is used connect django with home html file through an http request

"""
def Home(request):  
    return render(request, '\Home\templates\Home.html')

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
def Skills(request):  
    return render(request, '\Skills\templates\Skills.html')


"""
Name Function: Tasks
type: Function 
Purpose:It is used connect django with Calender Tasks file through an http request

"""
def Tasks(request):  
    return render(request, '\features\Tasks\Tasks.html')