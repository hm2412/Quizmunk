from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
from app.models import Stats, Room, User, Classroom
from app.models.room import RoomParticipant
from app.helpers.decorators import is_tutor
from app.models.stats import QuestionStats
import csv
import datetime
from app.helpers.helper_functions import get_responses_by_player_in_room, get_all_responses_question, get_student_quiz_history, calculate_average_score, find_best_and_worst_scores, get_guest_responses, isCorrectAnswer


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
    questions_stats = QuestionStats.objects.filter(room=stats_obj.room)
    context = {
        "stats": stats_obj,
        "participants": participants,
        "questions_stats": questions_stats,
    }
    return render(request, "tutor/stats_detail.html", context)


@is_tutor
def csv_download_player(request, stats_id):
    stats_obj = get_object_or_404(Stats, id=stats_id, quiz__tutor=request.user)
    room = stats_obj.room
    participants = RoomParticipant.objects.filter(room=room).exclude(user__role__iexact="tutor")
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="player_stats_{room.join_code}.csv"'
    writer = csv.writer(response)
    writer.writerow(["Participant", "Joined At", "Score"])

    for participant in participants:
        if participant.user:
            identifier = participant.user.email_address
        else:
            identifier = f"Guest ({participant.guest_access.session_id[:8]})"
        writer.writerow([
            identifier,
            participant.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            participant.score
        ])
    return response


@is_tutor
def csv_download_question(request, stats_id):
    stats_obj = get_object_or_404(Stats, id=stats_id, quiz__tutor=request.user)
    question_stats = QuestionStats.objects.filter(room=stats_obj.room)
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="question_stats_{stats_obj.room.join_code}.csv"'
    writer = csv.writer(response)
    writer.writerow(["Question", "Total Responses", "Correct Responses", "Incorrect Responses", "Percentage Correct"])

    for qs in question_stats:
        question_text = getattr(qs.question, "question_text", "N/A")
        total = qs.responses_received
        correct = qs.correct_responses
        incorrect = qs.wrong_responses 
        percentage = qs.percentage_correct
        writer.writerow([question_text, total, correct, incorrect, f"{percentage:.2f}%"])
    return response


def player_responses(request, room_id, player_id):
    player = get_object_or_404(RoomParticipant, id = player_id)
    room = get_object_or_404(Room, id=room_id)
    stats = Stats.objects.filter(room=room).first()
    if player.user:
        responses = get_responses_by_player_in_room(player.user, room)
        identifier = player.user.email_address
    else:
        responses = get_guest_responses(player.guest_access, room)
        identifier = f"Guest ({player.guest_access.session_id[:8]})"
    correct_count = sum(1 for r in responses if r.correct)
    incorrect_count = len(responses) - correct_count
    context={
        "player": identifier, 
        "room": room, 
        "responses": responses,
        "stats_id": stats.id if stats else None,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count
    }

    return render(request, 'tutor/player_responses.html',context)


def question_responses(request, room_id, question_id):
    room = get_object_or_404(Room, id=room_id)
    questions = room.get_questions()
    question = next((q for q in questions if q.id == int(question_id)), None)
    if not question:
        raise Http404("Question not found.")
    stats = Stats.objects.filter(room=room).first()
    responses = sorted(get_all_responses_question(room, question), key=lambda r: r.timestamp)
    for response in responses:
        isCorrectAnswer(response)
    correct_count = sum(1 for r in responses if r.correct)
    incorrect_count = len(responses) - correct_count
    context={
        'room':room,
        'question':question,
        'responses':responses,
        "stats_id": stats.id if stats else None,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count
    }
    return render(request, 'tutor/question_responses.html',context)


@is_tutor
def classroom_stats_view(request, classroom_id):
    """show the list of the quizzes started by the tutor for a classroom"""
    classroom= get_object_or_404(Classroom, id=classroom_id)
    stats_list = Stats.objects.filter(room__classroom=classroom,quiz__tutor=request.user).order_by('-date_played')
    quiz_names = [stats.quiz.name for stats in stats_list]
    scores = [stats.mean_score for stats in stats_list]
    context={
        "classroom": classroom,
        "stats_list":stats_list,
        "quiz_names": quiz_names,
        "scores":scores,
    }
    return render(request, "tutor/classroom_stats.html", context)


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