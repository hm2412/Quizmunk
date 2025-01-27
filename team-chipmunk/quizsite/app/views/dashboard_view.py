from django.shortcuts import render
from quizsite.app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage

@redirect_unauthenticated_to_homepage
@is_student
def student_dashboard(request):
    return render(request, 'student_dashboard.html')

@redirect_unauthenticated_to_homepage
@is_tutor
def tutor_dashboard(request):
    #Placeholder Quizzes
    quizzes = [
        {
            "quiz_img": "https://cdn.shopify.com/s/files/1/0751/9489/2598/files/plaice-mhnnice-org-min.jpg?v=1686201288",
            "quiz_title": "Math Quiz 1",
            "quiz_description": "Test your math skills with this beginner-level quiz.",
        },
        {
            "quiz_img": "https://www.marlin.ac.uk/assets/images/marlin/species/web/o_hlatham20090212_6.jpg",
            "quiz_title": "Science Quiz 2",
            "quiz_description": "Explore the wonders of science in this exciting quiz.",
        },
        {
            "quiz_img": "https://via.placeholder.com/300",
            "quiz_title": "History Quiz 3",
            "quiz_description": "Challenge yourself with this deep dive into history.",
        },
        {
            "quiz_img": "https://via.placeholder.com/300",
            "quiz_title": "Geography Quiz 4",
            "quiz_description": "Test your knowledge of world geography.",
        },
        {
            "quiz_img": "https://via.placeholder.com/300",
            "quiz_title": "Math Quiz 1",
            "quiz_description": "Test your math skills with this beginner-level quiz.",
        }
    ]
    # this is what the code should be once it acc works quizzes = Quiz.objects.filter(tutorID=request.user.id).order_by('-ID')[:5]


    return render(request, 'tutor_dashboard.html', {"quizzes": quizzes})
