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
    """stats_list = [
       {'id': 1, 'quiz': {'title': 'Python Basics Quiz'}, 'date_played': datetime.datetime(2025, 3, 11, 14, 30)},
       {'id': 2, 'quiz': {'title': 'Django Fundamentals'}, 'date_played': datetime.datetime(2025, 3, 10, 10, 15)},
        {'id': 3, 'quiz': {'title': 'Machine Learning Concepts'}, 'date_played': datetime.datetime(2025, 3, 9, 16, 45)},
    ]"""
    return render(request, "tutor/stats.html", {"stats_list": stats_list})


@is_tutor
def stats_details(request, stats_id):
    """show the stats for the live quiz"""
    stats_obj = get_object_or_404(Stats, id=stats_id, quiz__tutor=request.user)
    participants = RoomParticipant.objects.filter(room=stats_obj.room)
    """
    # Fake quizzes mapped by ID
    fake_stats_data = {
        1: {"id": 1, "quiz": {"title": "Python Basics Quiz"}, "date_played": datetime.datetime(2025, 3, 11, 14, 30), "num_participants": 3, "mean_score": 85.67, "median_score": 90.00},
        2: {"id": 2, "quiz": {"title": "Django Fundamentals"}, "date_played": datetime.datetime(2025, 3, 10, 10, 15), "num_participants": 5, "mean_score": 78.45, "median_score": 80.00},
        3: {"id": 3, "quiz": {"title": "Machine Learning Concepts"}, "date_played": datetime.datetime(2025, 3, 9, 16, 45), "num_participants": 4, "mean_score": 88.75, "median_score": 85.50},
    }
    # Fetch the correct fake quiz using `stats_id`
    stats_obj = fake_stats_data.get(int(stats_id), None)
    
    if not stats_obj:
        return HttpResponse("Quiz stats not found.", status=404)

    # Fake participants mapped by quiz ID
    fake_participants = {
        1: [
            {"user": {"email_address": "student1@example.com"}, "joined_at": "2025-03-11 14:35", "score": 92},
            {"user": {"email_address": "student2@example.com"}, "joined_at": "2025-03-11 14:37", "score": 78},
            {"guest_access": {"session_id": "abcd1234"}, "joined_at": "2025-03-11 14:40", "score": 87},
        ],
        2: [
            {"user": {"email_address": "learner1@example.com"}, "joined_at": "2025-03-10 10:05", "score": 75},
            {"user": {"email_address": "learner2@example.com"}, "joined_at": "2025-03-10 10:10", "score": 82},
        ],
        3: [
            {"user": {"email_address": "ml_student@example.com"}, "joined_at": "2025-03-09 16:50", "score": 95},
            {"guest_access": {"session_id": "xyz7890"}, "joined_at": "2025-03-09 16:55", "score": 88},
        ],
    }

    participants = fake_participants.get(int(stats_id), [])
    """
    context = {
        "stats": stats_obj,
        "participants": participants
    }
    return render(request, "tutor/stats_detail.html", context)

"""@is_tutor
def csv_download(request, stats_id):
    #Generate a CSV file for fake quiz stats

    # Fake stats data mapped by quiz ID
    fake_stats_data = {
        1: {"quiz": {"title": "Python Basics Quiz"}, "date_played": datetime.datetime(2025, 3, 11, 14, 30)},
        2: {"quiz": {"title": "Django Fundamentals"}, "date_played": datetime.datetime(2025, 3, 10, 10, 15)},
        3: {"quiz": {"title": "Machine Learning Concepts"}, "date_played": datetime.datetime(2025, 3, 9, 16, 45)},
    }

    # Fake participants mapped by quiz ID
    fake_participants = {
        1: [
            {"user": {"email_address": "student1@example.com"}, "joined_at": "2025-03-11 14:35", "score": 92},
            {"user": {"email_address": "student2@example.com"}, "joined_at": "2025-03-11 14:37", "score": 78},
            {"guest_access": {"session_id": "abcd1234"}, "joined_at": "2025-03-11 14:40", "score": 87},
        ],
        2: [
            {"user": {"email_address": "learner1@example.com"}, "joined_at": "2025-03-10 10:05", "score": 75},
            {"user": {"email_address": "learner2@example.com"}, "joined_at": "2025-03-10 10:10", "score": 82},
        ],
        3: [
            {"user": {"email_address": "ml_student@example.com"}, "joined_at": "2025-03-09 16:50", "score": 95},
            {"guest_access": {"session_id": "xyz7890"}, "joined_at": "2025-03-09 16:55", "score": 88},
        ],
    }

    # Fetch the correct fake quiz and participants
    stats_obj = fake_stats_data.get(int(stats_id), None)
    participants = fake_participants.get(int(stats_id), [])

    if not stats_obj:
        return HttpResponse("Quiz stats not found.", status=404)

    # Create CSV response
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="quiz_stats_fake_{stats_id}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Participant", "Joined At", "Score"])

    # Write fake participant data to CSV
    for participant in participants:
        if "user" in participant:
            identifier = participant["user"]["email_address"]
        else:
            identifier = f"Guest ({participant['guest_access']['session_id'][:8]})"
        writer.writerow([identifier, participant["joined_at"], participant["score"]])

    return response

"""
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

def player_responses(request, room_id,player_id):
    room = get_object_or_404(Room, id=room_id)
    player = get_object_or_404(User, id = player_id)

    responses = get_responses_by_player_in_room(player,room)

    context={
        'room':room,
        'player':player,
        'responses':responses,
    }
    return render(request, 'player_responses.html',context)

def player_responses(request, room_id,question_id):
    room = get_object_or_404(Room, id=room_id)
    question = get_object_or_404(User, id = question_id)

    responses = get_responses_by_player_in_room(question,room)

    context={
        'room':room,
        'question':question,
        'responses':responses,
    }
    return render(request, 'question_responses.html',context)

def student_stats(request,student_id):

    student= get_object_or_404(User, id=student_id)
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

    return render(request, 'student_stats.html', context)

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
