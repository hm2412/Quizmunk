from django.shortcuts import render

def student_dashboard(request):
    return render(request, 'student_dashboard.html')

def tutor_dashboard(request):
    return render(request, 'tutor_dashboard.html')
