from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from drf_yasg.openapi import Response as ResponceYASG
from drf_yasg.utils import swagger_auto_schema

from .models import Quiz, Question, QuestionItem
from .serializers import (
    QuizSerializer,
    QuizRetreiveSerializer,
    QuestionCreateSerializer,
    QuestionUpdateSerializer,
    QuestionSerializer,
    QuestionItemSerializer,
    QuizPassSerializer,
    QuizUserResultSerializer
)
from .services import prepare_question_data_to_output


class QuizCreateUpdateRemoveView(ModelViewSet):
    """Добавление, изменение, удаление опросов"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description='Create quiz',
    )
    def create(self, request, *args, **kwargs):
        return super(QuizCreateUpdateRemoveView, self).create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description='Update quiz',
    )
    def update(self, request, *args, **kwargs):
        return super(QuizCreateUpdateRemoveView, self).update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description='Partial update quiz',
    )
    def partial_update(self, request, *args, **kwargs):
        return super(QuizCreateUpdateRemoveView, self).partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description='Delete quiz',
    )
    def destroy(self, request, *args, **kwargs):
        return super(QuizCreateUpdateRemoveView, self).destroy(request, *args, **kwargs)


class QuizRetrieveView(ModelViewSet):
    """Получение списка активных опросов"""
    queryset = Quiz.objects.all().prefetch_related('questions')
    serializer_class = QuizRetreiveSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description='Retrieve all quizzes',
    )
    def list(self, request, *args, **kwargs):
        super(QuizRetrieveView, self).list( request, *args, **kwargs)


class QuizQuestionCreateView(APIView):
    """Добавление вопросов для опроса"""
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        request_body=QuestionCreateSerializer,
        operation_description='Add some questions to quiz',
    )
    def post(self, request, quiz):
        data = request.data.copy()
        data['quiz'] = quiz
        serializer = QuestionCreateSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(prepare_question_data_to_output(instance, serializer.validated_data))
        else:
            return Response(serializer.errors)


class QuizQuestionUpdateRemoveView(APIView):
    """Изменение, удаление вопросов"""
    permission_classes = [IsAdminUser]
    serializer_class = QuestionUpdateSerializer

    @staticmethod
    def get_object(pk):
        try:
            return Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        request_body=QuestionUpdateSerializer,
        operation_description='Delete question of quiz',
    )
    def delete(self, request, question: int):
        """Удаление вопроса"""
        question = self.get_object(question)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=QuestionUpdateSerializer,
        operation_description='Update partial question of quiz',
    )
    def put(self, request, question: int):
        """Обновление вопроса"""
        instance = self.get_object(question)
        serializer = QuestionUpdateSerializer(instance, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            data = serializer.data.copy()
            del data['quiz']
            return Response(prepare_question_data_to_output(instance, data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={200: QuestionUpdateSerializer},
        operation_description='Get detail about question of quiz',
    )
    def get(self, request, question: int):
        instance = self.get_object(question)
        serializer = QuestionSerializer(instance)
        data = serializer.data.copy()
        del data['id']
        return Response(prepare_question_data_to_output(instance, data))


class QuestionItemnUpdateRemoveView(APIView):
    """Изменение, удаление вариантов ответа на вопросы"""
    permission_classes = [IsAdminUser]
    serializer_class = QuestionItemSerializer

    @staticmethod
    def get_object(pk):
        try:
            return QuestionItem.objects.get(pk=pk)
        except QuestionItem.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        request_body=QuestionItemSerializer,
        operation_description='Delete one answer from answers questions',
    )
    def delete(self, request, question_item: int):
        """Удаление"""
        instance = self.get_object(question_item)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=QuestionItemSerializer,
        operation_description='Update one answer from answers questions',
    )
    def put(self, request, question_item: int):
        instance = self.get_object(question_item)
        serializer = QuestionItemSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizPassView(APIView):
    """Прохождение опроса"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=QuizPassSerializer,
        operation_description='Quiz pass',
    )
    def post(self, request):
        serializer = QuizPassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(request.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizUserResultView(APIView):
    """Получение детализации пройденных пользователем опросов"""
    permission_classes = [AllowAny]
    serializer_class = QuizUserResultSerializer

    @swagger_auto_schema(
        responses={
            200: ResponceYASG('test', QuizUserResultSerializer)
        },
        operation_description='Retrieve detail information of user passed quizzes',
    )
    def get(self, request, user: str):
        serializer = QuizUserResultSerializer(data={'user': user})
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
