from django.shortcuts import render, redirect, get_object_or_404
from app.helpers.decorators import is_student, redirect_unauthenticated_to_homepage
from django.contrib import messages
from app.models import Room

def join_quiz(request): #to enter the codes
    if request.method == 'POST':
        join_code = request.POST.get('join_code')  
        
        try:
            room = Room.objects.get(join_code=join_code)  
            return redirect('lobby', join_code=join_code) 
        except Room.DoesNotExist:
            messages.error(request, 'Invalid code. Please try again.')  

    return render(request, 'join.html')
