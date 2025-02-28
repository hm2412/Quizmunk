from app.models import Quiz, Question, IntegerInputQuestion, TrueFalseQuestion

def getAllQuestions(quiz):
    if isinstance(quiz, Quiz):
        questions_int = list(IntegerInputQuestion.objects.filter(quiz=quiz))
        questions_tf = list(TrueFalseQuestion.objects.filter(quiz=quiz))
        return questions_int + questions_tf