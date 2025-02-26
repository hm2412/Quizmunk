from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from app.models.classroom import Classroom, ClassroomStudent, ClassroomInvitation
from app.models.user import User
from django.contrib import messages

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
    students = ClassroomStudent.objects.filter(classroom_id=classroom_id).select_related("student")
    student_details = []
    # for cs in students:
    #     student_details.append(cs.student.first_name + cs.student.last_name +  "-" + cs.student.email_address)
    if request.method == 'POST':
        student_email = request.POST.get("student_email")
        try:
            student = User.objects.get(email_address=student_email, role=User.STUDENT)
            if students.filter(student=student).exists():
                messages.error(request, 'Student is already in this classroom')
                print("Student is already in classroom")
                # return redirect('classroom_detail_view', classroom_id=classroom.id)
            else:
                existing_invite = ClassroomInvitation.objects.filter(classroom=classroom, student=student, status="pending").exists()
                if existing_invite:
                    messages.error(request, 'Invite already sent to this student')
                    print("Invite was already sent to this student")
                    # return redirect('classroom_detail_view', classroom_id=classroom.id)
                
                else:
                    # Create the invitation
                    ClassroomInvitation.objects.create(classroom=classroom, student=student)
                    messages.success(request, f'Invitation sent to {student.email_address}')
                    print("Invitation sent to student.")
        except User.DoesNotExist:
            messages.error(request, 'No student found with that email')
            print("No student found with that email")
        # classroom.delete()
        # return redirect('classroom_detail_view', classroom_id=classroom.id)
    
    return render(request, 'tutor/classroom_detail.html', {
        'classroom': classroom,
        'student_count': classroom.students.count(),
        'students': students
    })
