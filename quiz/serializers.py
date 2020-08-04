from rest_framework import serializers

from .models import Quiz, Question, QuestionItem, TYPE_ANSWER, Answer, User
from .services import QuestionCreateController, QuestionUpdateController, AnswerCreateController, \
    QuizUserResultController
from .errors import ERRORS


class QuestionTypeValidationMixin:
    def validation(self, attrs):
        if attrs.get('type') in ('answer_one_selected', 'answer_some_selected'):
            try:
                if len(attrs.get('question_item')) == 1:
                    if attrs.get('question_item')[0] == '':
                        raise serializers.ValidationError(ERRORS['error_question_item_is_not_exist'])
            except TypeError:
                raise serializers.ValidationError(ERRORS['error_question_item_is_not_exist'])
        elif attrs.get('question_item') is not None:
            raise serializers.ValidationError(ERRORS['error_question_item_not_necessary'])
        return attrs


class QuizSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Quiz"""
    class Meta:
        model = Quiz
        fields = ['pk', 'name', 'start_date', 'finish_date', 'description']

    def update(self, instance, validated_data):
        if validated_data.get('start_date'):
            raise serializers.ValidationError(ERRORS['error_change_start_date'])
        return super(QuizSerializer, self).update(instance, validated_data)


class QuestionCreateSerializer(serializers.Serializer, QuestionTypeValidationMixin):
    """Сериалайзер для модели Question"""
    quiz = serializers.IntegerField()
    text = serializers.CharField()
    type = serializers.ChoiceField(choices=TYPE_ANSWER)
    question_item = serializers.ListField(required=False)

    def create(self, validated_data):
        """Создание нового вопроса для опроса"""
        questioncreate_controller = QuestionCreateController(validated_data)
        question = questioncreate_controller.create()
        return question


class QuestionUpdateSerializer(serializers.Serializer, QuestionTypeValidationMixin):
    quiz = QuizSerializer(required=False, read_only=True)
    text = serializers.CharField(required=False)
    type = serializers.ChoiceField(choices=TYPE_ANSWER, required=False)
    question_item = serializers.ListField(required=False)

    def validate(self, attrs):
        return self.validation(attrs)

    def update(self, instance, validated_data):
        questionupdate_controller = QuestionUpdateController(validated_data, instance)
        question = questionupdate_controller.update()
        return question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuestionItemSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(required=False, read_only=True)

    class Meta:
        model = QuestionItem
        fields = ['pk','name', 'question']
        read_only = ['question', 'pk']


class QuizRetreiveSerializer(serializers.ModelSerializer):
    """Сериалайзер  для модели Quiz"""
    questions = QuestionSerializer(read_only=True, many=True)
    question_items = QuestionItemSerializer(read_only=True, many=True)

    class Meta:
        model = Quiz
        fields = ['pk', 'name', 'start_date', 'finish_date', 'description', 'questions', 'question_items']
        depth = 4


class AnswerSerializer(serializers.ModelSerializer):
    """Сеариализатор отвчетов"""

    class Meta:
        model = Answer
        fields = ['text', 'question', 'answer_selected']


class QuizPassSerializer(serializers.Serializer):
    """Сериализатор 'прохождения опросов'"""
    user = serializers.CharField()
    questions = serializers.ListField(child=AnswerSerializer())

    def validate(self, attrs):
        for question_item in attrs['questions']:
            if question_item['question'].type == 'answer_text':
                if not isinstance(question_item['text'], str):
                    raise serializers.ValidationError(ERRORS['error_question_answer_text_is_empty'])
            elif question_item['question'].type in ('answer_one_selected', 'answer_some_selected'):
                if len(question_item['answer_selected']) == 0:
                    raise serializers.ValidationError(ERRORS['error_question_answer_items_length_is_zero'])
                elif question_item['question'].type == 'answer_one_selected':
                    if len(question_item['answer_selected']) > 1:
                        raise serializers.ValidationError(ERRORS['error_question_answer_items_length_is_more_one'])

            question_items_list = QuestionItem.objects.filter(question=question_item['question']).values_list('pk', flat=True)
            for answer_item in question_item['answer_selected']:
                if answer_item.pk not in question_items_list:
                    raise serializers.ValidationError(ERRORS['error_question_answer_items_not_belong_to_question'])
        return attrs

    def create(self, validated_data):
        answer = AnswerCreateController(validated_data)
        return answer.create()


class AnswerSchemaSerializer(serializers.Serializer):
    """Сериализатор необходим для вывода представления результата GET /quizzes/users/{user}/ OpenAPI"""
    id = serializers.IntegerField()
    text = serializers.CharField()
    answer_selected = serializers.ListField(serializers.CharField(allow_null=True), required=False)


class AnswerToQuestionSchemaSerializer(serializers.Serializer):
    """Сериализатор необходим для вывода представления результата GET /quizzes/users/{user}/ OpenAPI"""
    id = serializers.IntegerField(required=False)
    text = serializers.CharField(allow_null=True)
    answers = serializers.ListField(child=serializers.CharField(), allow_null=True)


class QuizDetailShemaSerializer(serializers.Serializer):
    """Сериализатор необходим для вывода представления результата GET /quizzes/users/{user}/ OpenAPI"""
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    questions = serializers.ListField(child=AnswerToQuestionSchemaSerializer(), required=False)


class QuizShemaSerializer1(serializers.Serializer):
    """Сериализатор необходим для вывода представления результата GET /quizzes/users/{user}/ OpenAPI"""
    quiz = serializers.DictField(child=QuizDetailShemaSerializer())


class QuizUserResultSerializer(serializers.Serializer):
    """Сериализация пройденных пользователем опросов"""
    user = serializers.CharField()
    results_quizzes = serializers.ListField(child=QuizShemaSerializer1(), required=False)

    def validate_user(self, value):
        try:
            user = User.objects.get(name=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(ERRORS['error_user_does_not_exist'])
        return user

    def validate(self, attrs):
        result = {}
        quiz_user_result = QuizUserResultController(attrs['user'])
        result['user'] = attrs['user']
        result['results_quizzes'] = quiz_user_result.reports()
        return result

    def to_representation(self, instance):
        results_quizzes = instance['results_quizzes']
        print(f"instance {instance}")
        ret = super(QuizUserResultSerializer, self).to_representation(instance)
        ret['results_quizzes'] = results_quizzes
        return ret