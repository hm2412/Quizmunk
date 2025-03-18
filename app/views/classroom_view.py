from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage
from app.models.classroom import Classroom, ClassroomStudent, ClassroomInvitation
from app.models.user import User
from django.contrib import messages

@login_required
@is_student
def accept_classroom_invite(request, invite_id):
    invite = get_object_or_404(ClassroomInvitation, id=invite_id, student=request.user, status='pending')
    if request.method == 'POST' and request.POST.get('action') == 'accept':
        #create the classroom student object
        ClassroomStudent.objects.create(classroom=invite.classroom, student=request.user)

        invite.status = 'accepted'
        invite.save()
        
        return redirect('student_classroom_view')

@is_student
def decline_classroom_invite(request, invite_id):
    invite = get_object_or_404(ClassroomInvitation, id=invite_id, student=request.user, status='pending')
    if request.method == 'POST' and request.POST.get('action') == 'decline':
        invite.status = 'declined'
        invite.save()
        
        return redirect('student_classroom_view')
    
@login_required
@is_student
def student_classroom_view(request):
    # classrooms = ClassroomStudent.objects.filter(student=request.user)
    classrooms = Classroom.objects.filter(
        students__student=request.user
    ).distinct()
    
    invites = ClassroomInvitation.objects.filter(student=request.user, status='pending')
    for invite in invites:
        invite.classroom_name = invite.classroom.name
        invite.tutor_name = invite.classroom.tutor.first_name + ' ' + invite.classroom.tutor.last_name
    return render(request, 'student/classrooms.html', {'classrooms': classrooms, 'invites':invites})

@login_required
@is_student
def student_classroom_detail_view(request, classroom_id):
    if ClassroomStudent.objects.filter(classroom_id=classroom_id, student=request.user).exists():
        classroom = get_object_or_404(Classroom, id=classroom_id)
    else:
        raise Http404("Classroom not found or you are not a student in it.")
    return render(request, 'student/classroom_detail.html', {'classroom':classroom})

@login_required
@is_tutor
def tutor_classroom_view(request):
    classrooms = Classroom.objects.filter(tutor=request.user)
    #either make a completely 
    
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
            return redirect('tutor_classroom_view')
    
    return render(request, 'tutor/classroom_view.html', {'classrooms': classrooms})

@login_required
@is_tutor
def tutor_classroom_detail_view(request, classroom_id):
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
