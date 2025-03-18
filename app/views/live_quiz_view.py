from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from app.models import Quiz, RoomParticipant, Room, GuestAccess, QuizState
from app.helpers.decorators import is_tutor
from app.helpers.helper_functions import getAllQuestions
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt


def get_room(join_code):
    return get_object_or_404(Room, join_code=join_code)


@is_tutor
def tutor_live_quiz(request, quiz_id, join_code):
    room = get_room(join_code)
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    all_questions = quiz.get_all_questions()
    first_question = all_questions[0] if all_questions else None
    participants = RoomParticipant.objects.filter(room=room)
    participantNumber = participants.count()

    context = {
        'quiz': quiz,
        'first_question': first_question,
        'questions': all_questions,
        'room': room,
        'join_code': join_code,
        'participants': participants,
        'participant_number': participantNumber,
    }

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"lobby_{join_code}",
        {
            "type": "quiz_started",
            "student_quiz_url": f"/student/live-quiz/{join_code}/",
            "tutor_quiz_url": f"/live-quiz/{quiz_id}/{join_code}",
        }
    )
    return render(request, 'tutor/live_quiz.html', context)


def student_live_quiz(request, room_code):
    room = get_object_or_404(Room, join_code=room_code)
    if request.user.is_authenticated and request.user.role.lower() != "tutor":
        participant, created = RoomParticipant.objects.get_or_create(room=room, user=request.user)
    else:
        guest_session = request.session.session_key
        if not guest_session:
            request.session.save()
            guest_session = request.session.session_key
        from app.models.guest import GuestAccess
        guest_access, _ = GuestAccess.objects.get_or_create(session_id=guest_session)
        participant, created = RoomParticipant.objects.get_or_create(room=room, guest_access=guest_access)
    participants = RoomParticipant.objects.filter(room=room).exclude(user__role__iexact="tutor")
    participant_number = participants.count()
    context = {
        'room': room,
        'participants': participants,
        'participant_number': participant_number
    }
    return render(request, 'student/student_live_quiz.html', context)


def start_quiz(request, join_code):
    room = get_object_or_404(Room, join_code=join_code)

    if request.method == "POST":
        room.current_question_index = 0
        room.is_quiz_active = True
        room.save()

        return JsonResponse({
            "status": "success",
            "message": "Quiz started",
            "first_question": room.get_current_question().question_text
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def next_question(request, join_code):

    # Ensure the room exists
    room = get_room(join_code)
    if not room:
        return JsonResponse({"error": "Room not found."}, status=400)

    # Ensure the quiz state exists
    quiz_state = QuizState.objects.filter(room=room).first()
    if not quiz_state:
        return JsonResponse({"error": "Quiz has not started for this room."}, status=400)

    # Ensure the quiz has started
    if not quiz_state.quiz_started:
        return JsonResponse({"error": "Quiz has not started for this room."}, status=400)

    # Process only POST requests
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    # Retrieve questions
    quiz = room.quiz
    questions = getAllQuestions(quiz)

    # Check if there are more questions
    if quiz_state.current_question_index < len(questions):
        current_question = questions[quiz_state.current_question_index]
        quiz_state.current_question_index += 1
        quiz_state.save()
        return JsonResponse({
            "question_number": quiz_state.current_question_index,
            "question": current_question.question_text,
            # "answer": current_question.correct_answer
        })
    else:
        return JsonResponse({"message": "No more questions!"})


@csrf_exempt
def end_quiz(request, join_code):
    room = get_room(join_code)
    quiz_state = QuizState.objects.filter(room=room).first()
    if request.method == "POST":
        if quiz_state:
            quiz_state.current_question_index = -1
            quiz_state.quiz_started = False
            quiz_state.save()
            return JsonResponse({"message": "Quiz ended!"})
        return JsonResponse({"error": "Quiz not found for this room."}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)