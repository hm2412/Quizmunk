from app.forms import (
    #add more forms here
    IntegerInputQuestionForm, 
    TrueFalseQuestionForm,
    )
from app.forms.text_input_question_form import TextInputQuestionForm
from app.forms.multiple_choice_question_form import MultipleChoiceQuestionForm
from app.forms.numerical_range_question_form import NumericalRangeQuestionForm
from app.forms.decimal_input_question_form import DecimalInputQuestionForm
from app.forms.sorting_question_form import SortingQuestionForm
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
    'text': TextInputQuestionForm,
    'multiple_choice': MultipleChoiceQuestionForm,
    'numerical_range': NumericalRangeQuestionForm,
    'decimal': DecimalInputQuestionForm,
    'sorting': SortingQuestionForm
}

QUESTION_MODELS = {
    #add models here
    'integer': IntegerInputQuestion,
    'true_false': TrueFalseQuestion,
    'text': TextInputQuestion,
    'multiple_choice': MultipleChoiceQuestion,
    'numerical_range': NumericalRangeQuestion,
    'decimal': DecimalInputQuestion,
    'sorting': SortingQuestion
}
