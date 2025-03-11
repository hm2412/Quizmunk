from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage
from app.models.classroom import Classroom, ClassroomStudent, ClassroomInvitation
from app.models.room import Room
from app.models.user import User
from app.models.quiz import Quiz
from django.contrib import messages

@redirect_unauthenticated_to_homepage
@is_student
def accept_classroom_invite(request, invite_id):
    invite = get_object_or_404(ClassroomInvitation, id=invite_id, student=request.user, status='pending')
    if request.method == 'POST' and request.POST.get('action') == 'accept':
        #create the classroom student object
        ClassroomStudent.objects.create(classroom=invite.classroom, student=request.user)

        invite.status = 'accepted'
        invite.save()
        
        return redirect('student_classroom_view')

@redirect_unauthenticated_to_homepage
@is_student
def decline_classroom_invite(request, invite_id):
    invite = get_object_or_404(ClassroomInvitation, id=invite_id, student=request.user, status='pending')
    if request.method == 'POST' and request.POST.get('action') == 'decline':
        invite.status = 'declined'
        invite.save()
        
        return redirect('student_classroom_view')

@redirect_unauthenticated_to_homepage
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

@redirect_unauthenticated_to_homepage
@is_student
def student_classroom_detail_view(request, classroom_id):
    if ClassroomStudent.objects.filter(classroom_id=classroom_id, student=request.user).exists():
        classroom = get_object_or_404(Classroom, id=classroom_id)
        room = Room.objects.filter(classroom=classroom).first()
    else:
        raise Http404("Classroom not found or you are not a student in it.")
    return render(request, 'student/classroom_detail.html', {'classroom':classroom, 'room': room})

@redirect_unauthenticated_to_homepage
@is_tutor
def tutor_classroom_view(request):
    classrooms = Classroom.objects.filter(tutor=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('classroom_name')
        description = request.POST.get('description')
        
        if name and description:
            new_classroom = Classroom.objects.create(
                name=name,
                description=description,
                tutor=request.user
            )
            new_classroom.save()
            return redirect('tutor_classroom_view')
    
    return render(request, 'tutor/classroom_view.html', {'classrooms': classrooms})

@redirect_unauthenticated_to_homepage
@is_tutor
def tutor_classroom_detail_view(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, tutor=request.user)
    students = ClassroomStudent.objects.filter(classroom_id=classroom_id).select_related("student")
    pending_invites = ClassroomInvitation.objects.filter(
        classroom=classroom,
        status='pending'
    ).select_related('student')
    quizzes = Quiz.objects.filter(tutor=request.user).order_by("-id")
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'remove_student':
            student_id = request.POST.get('student_id')
            try:
                student_enrollment = ClassroomStudent.objects.get(
                    classroom=classroom,
                    student_id=student_id
                )
                student_enrollment.delete()
                return redirect('tutor_classroom_detail', classroom_id=classroom.id)
            except ClassroomStudent.DoesNotExist:
                pass
                
        elif action == 'edit_description':
            new_description = request.POST.get('description', '').strip()
            if new_description:
                classroom.description = new_description
                classroom.save()
            return redirect('tutor_classroom_detail', classroom_id=classroom.id)
            
        else:
            # Existing invite student logic
            student_email = request.POST.get("student_email", "").strip()
            if not student_email:
                messages.error(request, 'Please enter an email address')
                return redirect('tutor_classroom_detail', classroom_id=classroom.id)
            
            try:
                user = User.objects.get(email_address=student_email)
                
                if user.role != User.STUDENT:
                    messages.error(request, 'This email belongs to a tutor account')
                    return redirect('tutor_classroom_detail', classroom_id=classroom.id)
                
                if ClassroomStudent.objects.filter(classroom=classroom, student=user).exists():
                    messages.error(request, 'This student is already in your classroom')
                    return redirect('tutor_classroom_detail', classroom_id=classroom.id)
                
                if ClassroomInvitation.objects.filter(
                    classroom=classroom, 
                    student=user, 
                    status="pending"
                ).exists():
                    messages.error(request, 'You have already invited this student')
                    return redirect('tutor_classroom_detail', classroom_id=classroom.id)
                
                ClassroomInvitation.objects.create(classroom=classroom, student=user)
                return redirect('tutor_classroom_detail', classroom_id=classroom.id)
                
            except User.DoesNotExist:
                messages.error(request, 'No account exists with this email')
                return redirect('tutor_classroom_detail', classroom_id=classroom.id)
    
    return render(request, 'tutor/classroom_detail.html', {
        'classroom': classroom,
        'student_count': classroom.students.count(),
        'students': students,
        'pending_invites': pending_invites,
        'quizzes': quizzes
    })
