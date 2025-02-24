from app.forms import (
    #add more forms here
    IntegerInputQuestionForm, 
    TrueFalseQuestionForm,
    )
from app.models.quiz import (
    #add more models here
    IntegerInputQuestion, 
    TrueFalseQuestion, 
    TextInputQuestion, 
    DecimalInputQuestion, 
    MultipleChoiceQuestion, 
    NumericalRangeQuestion, 
    SortingQuestion
)

QUESTION_FORMS = {
    #add the forms here
    'integer': IntegerInputQuestionForm,
    'true_false': TrueFalseQuestionForm,
}

QUESTION_MODELS = {
    #add models here
    'integer': IntegerInputQuestion,
    'true_false': TrueFalseQuestion,
}