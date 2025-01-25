from django.contrib.auth.decorators import user_passes_test

def is_student(user):
    return user.is_authenticated and user.role == "student"

def is_tutor(user):
    return user.is_authenticated and user.role == "tutor"

def login_required(view_func):
    return user_passes_test(lambda user: user.is_authenticated, login_url='/login/')(view_func)
