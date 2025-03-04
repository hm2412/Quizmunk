from app.models import Quiz, IntegerInputQuestion, TrueFalseQuestion, NumericalRangeResponse


def getAllQuestions(quiz):
    if isinstance(quiz, Quiz):
        questions_int = list(IntegerInputQuestion.objects.filter(quiz=quiz))
        questions_tf = list(TrueFalseQuestion.objects.filter(quiz=quiz))
        return questions_int + questions_tf
    return None

def isCorrectAnswer(response):
    if isinstance(response, NumericalRangeResponse):
        return response.question.min_value <= response.answer <= response.question.max_value

    else:
        return response.answer == response.question.correct_answer
