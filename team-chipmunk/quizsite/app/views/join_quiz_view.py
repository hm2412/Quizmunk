from django.shortcuts import render

def join_quiz_view(request):
    return render(request, 'join.html')