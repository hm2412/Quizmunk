from django.shortcuts import redirect,render, get_object_or_404
from app.models import Quiz, RoomParticipant, Room, Question, IntegerInputQuestion, TrueFalseQuestion
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

from django.views.decorators.csrf import csrf_exempt

QUESTIONS = [
    {"question": "What is the capital of France?", "answer": "Paris"},
    {"question": "What is 2 + 2?", "answer": "4"},
    {"question": "What is the largest ocean?", "answer": "Pacific Ocean"},
]
quiz_state = {}

def tutor_live_quiz(request, join_code):
    room = get_object_or_404(Room, join_code=join_code)
    leaders = RoomParticipant.objects.filter(room=room).order_by('-score')[:10]  

    return render(request, 'tutor/live_quiz.html', {'leaders': leaders, 'room': room})

def start_quiz(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    quiz = room.quiz  # Get the quiz associated with the room
    questions_int = list(IntegerInputQuestion.objects.filter(quiz=quiz))
    questions_tf = list(TrueFalseQuestion.objects.filter(quiz=quiz))
    questions = questions_int + questions_tf

    if not questions:
        return JsonResponse({"error": "No questions found for this quiz."}, status=400)

    if request.method == "POST":
        quiz_state[room_id] = {
            "current_question": 0,
            "quiz_started": True,
            "questions": questions
        }
        return JsonResponse({"message": "Quiz started!"})
    return JsonResponse({"error": "Invalid request"}, status=400)

'''@csrf_exempt
def next_question(request, room_id):
    if room_id not in quiz_state or not quiz_state[room_id]["quiz_started"]:
        return JsonResponse({"error": "Quiz has not started for this room."}, status=400)

    if request.method == "POST":
        current_question_index = quiz_state[room_id]["current_question"]
        questions = quiz_state[room_id]["questions"]
        if current_question_index < len(questions):
            quiz_state[room_id]["current_question"] += 1
            question_data = questions[current_question_index]
            return JsonResponse({
                "question_number": current_question_index + 1,
                "question": question_data.question,  
                "answer": question_data.answer
            })
        else:
            return JsonResponse({"message": "No more questions!"})
    return JsonResponse({"error": "Invalid request"}, status=400)'''

@csrf_exempt
def next_question(request, room_id):
    # Check if the room has started the quiz
    if room_id not in quiz_state or not quiz_state[room_id]["quiz_started"]:
        return JsonResponse({"error": "Quiz has not started for this room."}, status=400)

    if request.method == "POST":
        # Check the state of the quiz for the room
        current_question_index = quiz_state[room_id]["current_question"]
        questions = quiz_state[room_id]["questions"]
        
        # Debugging: log the state of the quiz
        print(f"quiz_state: {quiz_state}")
        print(f"room_id: {room_id}")
        print(f"current_question_index: {current_question_index}")
        print(f"questions: {questions}")

        # Ensure there are still questions to show
        if current_question_index < len(questions):
            quiz_state[room_id]["current_question"] += 1
            question_data = questions[current_question_index]
            
            # Ensure the question and answer exist
            print(f"question_data: {question_data}")
            return JsonResponse({
                "question_number": current_question_index + 1,
                "question": question_data.question,  # Use dot notation to access the field
                "answer": question_data.answer  # Use dot notation to access the field
            })
        else:
            return JsonResponse({"message": "No more questions!"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def end_quiz(request, room_id):
    if request.method == "POST":
        if room_id in quiz_state:
            quiz_state[room_id]["current_question"] = -1
            quiz_state[room_id]["quiz_started"] = False
            return JsonResponse({"message": "Quiz ended!"})
        return JsonResponse({"error": "Quiz not found for this room."}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

