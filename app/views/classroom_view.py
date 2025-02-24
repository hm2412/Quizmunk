from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from app.models.classroom import Classroom

@login_required
def classroom_view(request):
    classrooms = Classroom.objects.filter(tutor=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('classroom_name')
        description = request.POST.get('description')
        
        if name and description:
            new_classroom = Classroom(
                name=name,
                description=description,
                tutor=request.user
            )
            new_classroom.save()
            return redirect('classroom_view')
    
    return render(request, 'tutor/classroom_view.html', {'classrooms': classrooms})

@login_required
def classroom_detail_view(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, tutor=request.user)
    
    if request.method == 'POST':
        classroom.delete()
        return redirect('classroom_view')
    
    return render(request, 'tutor/classroom_detail.html', {
        'classroom': classroom,
        'student_count': classroom.students.count()
    })
