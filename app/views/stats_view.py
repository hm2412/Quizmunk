from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from app.models.stats import Stats
from app.models.room import RoomParticipant
from app.helpers.decorators import is_tutor
import csv


@is_tutor
def stats_view(request):
    """show the list of the quizzes started by the tutor"""
    stats_list = Stats.objects.filter(quiz__tutor=request.user).order_by('-date_played')
    return render(request, "tutor/stats.html", {"stats_list": stats_list})


@is_tutor
def stats_details(request, stats_id):
    """show the stats for the live quiz"""
    stats_obj = get_object_or_404(Stats, id=stats_id, quiz__tutor=request.user)
    participants = RoomParticipant.objects.filter(room=stats_obj.room)
    context = {
        "stats": stats_obj,
        "participants": participants
    }
    return render(request, "tutor/stats_detail.html", context)


@is_tutor
def csv_download(request, stats_id):
    """genrate a csv file for the stats"""
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


