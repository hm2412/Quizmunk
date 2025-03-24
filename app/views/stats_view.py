from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from app.models import Stats, Room, User, Classroom
from app.models.room import RoomParticipant
from app.helpers.decorators import is_tutor
import csv
import datetime
from app.helpers.helper_functions import get_responses_by_player_in_room, get_all_responses_question, get_student_quiz_history, calculate_average_score, find_best_and_worst_scores


@is_tutor
def stats_view(request):
    """show the list of the quizzes started by the tutor"""
    stats_list = Stats.objects.filter(quiz__tutor=request.user).order_by('-date_played')
    return render(request, "tutor/stats.html", {"stats_list": stats_list})

@is_tutor
def stats_details(request, stats_id):
    """show the stats for the live quiz"""
    stats_obj = get_object_or_404(Stats, id=stats_id, quiz__tutor=request.user)
    participants = RoomParticipant.objects.filter(room=stats_obj.room).exclude(user__role__iexact="tutor")
    context = {
        "stats": stats_obj,
        "participants": participants
    }
    return render(request, "tutor/stats_detail.html", context)

@is_tutor
def csv_download(request, stats_id):
    #genrate a csv file for the stats
    
    stats_obj = get_object_or_404(Stats, id=stats_id, quiz__tutor=request.user)
    room = stats_obj.room
    participants = RoomParticipant.objects.filter(room=stats_obj.room)

    response = HttpResponse(content_type="text/csv")
    #this is the best way right now to seprate quizzes states as a quiz can create multiple live quizzes
    response['Content-Disposition'] = f'attachment; filename="quiz_stats_{room.join_code}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Participant", "Joined At", "Score"])

    for participant in participants:
        if participant.user:
            identifier = participant.user.email_address
        else:
            identifier = participant.guest_access.session_id[:8]
        writer.writerow([identifier, participant.joined_at, participant.score])

def player_responses(request, room_id, player_id):
    player = get_object_or_404(User, id = player_id)
    room = get_object_or_404(Room, id=room_id)
    stats = Stats.objects.filter(room=room).first()
    responses = get_responses_by_player_in_room(player,room)

    context={
        "player": player, 
        "room": room, 
        "responses": responses,
        "stats_id": stats.id if stats else None
    }

    return render(request, 'tutor/player_responses.html',context)

def question_responses(request, room_id,question_id):
    room = get_object_or_404(Room, id=room_id)
    question = get_object_or_404(User, id = question_id)
    stats = Stats.objects.filter(room=room).first()
    responses = get_responses_by_player_in_room(question,room)

    context={
        'room':room,
        'question':question,
        'responses':responses,
        "stats_id": stats.id if stats else None
    }
    return render(request, 'tutor/question_responses.html',context)

def student_stats(request,student_id):

    student= get_object_or_404(User, id=student_id)
    print("Student Object:", student)
    quiz_history= get_student_quiz_history(student)
    average_score = calculate_average_score(quiz_history)
    best_score, worst_score = find_best_and_worst_scores(quiz_history)

    context={
        'student': student,
        'quiz_history': quiz_history,
        'average_score': average_score,
        'best_score': best_score,
        'worst_score': worst_score,
    }

    return render(request, 'student/student_stats.html', context)

@is_tutor
def classroom_stats_view(request, classroom_id):
    """show the list of the quizzes started by the tutor for a classroom"""
    classroom= get_object_or_404(Classroom, id=classroom_id)
    stats_list = Stats.objects.filter(room__classroom=classroom,quiz__tutor=request.user).order_by('-date_played')
    context={
        "classroom": classroom,
        "stats_list":stats_list
    }
    return render(request, "tutor/classroom_stats.html", context)
