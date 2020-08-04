from django.urls import path

from .views import (
    QuizRetrieveView,
    QuizCreateUpdateRemoveView,
    QuizQuestionUpdateRemoveView,
    QuizQuestionCreateView,
    QuestionItemnUpdateRemoveView,
    QuizPassView,
    QuizUserResultView
)

urlpatterns = [
    path('quizzes/', QuizCreateUpdateRemoveView.as_view({
        'post': 'create',
    })),
    path('quizzes/all/', QuizRetrieveView.as_view({
        'get': 'list',
    })),
    path('quizzes/pass/', QuizPassView.as_view()),
    path('quizzes/<int:pk>/', QuizCreateUpdateRemoveView.as_view({
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    path('quizzes/<int:quiz>/questions/', QuizQuestionCreateView.as_view()),
    path('quizzes/questions/<int:question>/', QuizQuestionUpdateRemoveView.as_view()),
    path('quizzes/questions/question_item/<int:question_item>/', QuestionItemnUpdateRemoveView.as_view()),
    path('quizzes/users/<str:user>/', QuizUserResultView.as_view()),
]
