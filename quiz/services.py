from typing import Dict, List, Optional
from rest_framework import serializers

from .models import Question, QuestionItem, Quiz, User, Answer
from .errors import ERRORS


def check_quiz_is_exist(quiz_id: int) -> bool:
    """Проверка существования опроса"""
    try:
        Quiz.objects.get(pk=quiz_id)
        return True
    except Quiz.DoesNotExist:
        return False


def get_question_item_pk_and_name(question: Question) -> List[str]:
    """Формирование списка QuestionItem"""
    return [{'pk': item[0], 'name': item[1]} for item in QuestionItem.objects.filter(question=question).
        values_list('pk', 'name')]


def prepare_question_data_to_output(questin: Question, response_data: Dict[str, str]) -> Dict[str, str]:
    """Подготовка информации о Question перед отправкой пользователю"""
    data = {}
    data['pk'] = questin.pk
    data.update(response_data)
    data['question_item'] = get_question_item_pk_and_name(questin)
    return data


class QuizUserResultController:
    """Формировнаие результата пройденных пользователем опросов с детализацией"""
    user: User
    questions: List
    answers_result: List

    def __init__(self, user):
        self.user = user
        self.questions = []
        self.answers_result = []

    def _add_questions_and_answers_rows_in_list(self, answers) -> None:
        self.questions.append({
            'id': answers.question.pk,
            'text': answers.question.text,
            'answers': {
                'id': answers.pk,
                'text': answers.text,
                'answer_selected': [answer.name for answer in answers.answer_selected.all()]
            }
        })

    def _add_questions_and_answers_list_into_result_list(self, answers, quiz_id: Optional) -> None:
        self.answers_result.append({
            'quiz': {
                'id': answers.question.quiz.pk if quiz_id is None else quiz_id,
                'name': answers.question.quiz.name,
                'questions': self.questions.copy()
            }
        })
        self.questions.clear()

    def reports(self):
        quiz_id = 0
        for answers in Answer.objects.filter(user=self.user).order_by('question__quiz'):
            print(f"quiz {answers.question.quiz.pk}")
            if quiz_id == 0:
                quiz_id = answers.question.quiz.pk
                self._add_questions_and_answers_rows_in_list(answers)
                continue

            if quiz_id == answers.question.quiz.pk:
                self._add_questions_and_answers_rows_in_list(answers)
            else:
                if len(self.questions) > 0 or len(self.answers):
                    self._add_questions_and_answers_list_into_result_list(answers, quiz_id)
                quiz_id = answers.question.quiz.pk
                self._add_questions_and_answers_rows_in_list(answers)
                self._add_questions_and_answers_list_into_result_list(answers, None)
        return self.answers_result


class AnswerCreateController:
    """Сохранение результата прохождения опроса"""
    data: Dict[str, str]

    def __init__(self, data):
        self.data = data

    def create(self) -> None:
        answers = []
        user, _ = User.objects.get_or_create(name=self.data['user'])
        for question_data in self.data['questions']:
            answer = Answer.objects.create(
                user=user,
                text=question_data['text'],
                question=question_data['question']
            )
            answer.answer_selected.set(question_data['answer_selected'])
            answers.append(answer)
        return answers


class QuestionItemCreateMixin:
    """Создание вариантов ответа на вопросы"""

    @staticmethod
    def _create_question_item(question: Question, list_questions: List[str]) -> None:
        for question_item in list_questions:
            QuestionItem(
                name=question_item,
                question=question
            ).save()


class QuestionCreateController(QuestionItemCreateMixin):
    """Создание вопросов для опроса"""
    data: Dict[str, str]

    def __init__(self, data):
        self.data = data

    def _create_with_answer_text(self) -> Question:
        """Создание вопроса с текстовым ответом"""
        quiz = Quiz.objects.get(pk=self.data['quiz'])
        question = Question(
            quiz=quiz,
            text=self.data['text'],
            type=self.data['type']
        )
        question.save()
        return question

    def _create_with_selected_answer(self) -> Question:
        """Создание вопроса с выбором вариантов ответов"""
        list_questions = self.data['question_item']
        del self.data['question_item']
        question = self._create_with_answer_text()
        self._create_question_item(question, list_questions)
        return question

    def create(self) -> Question:
        if check_quiz_is_exist(self.data['quiz']):
            if self.data.get('type') in ('answer_one_selected', 'answer_some_selected'):
                return self._create_with_selected_answer()
            elif self.data.get('type') == 'answer_text':
                return self._create_with_answer_text()
            else:
                raise serializers.ValidationError(ERRORS['error_type_question_is_not_exist'])
        else:
            raise serializers.ValidationError(ERRORS['error_quiz_is_not_exist'])


class QuestionUpdateController(QuestionItemCreateMixin):
    """Изменения вопросов"""
    data: Dict[str, str]
    instance: Question

    def __init__(self, data, instance):
        self.data = data
        self.instance = instance

    def _delete_all_question_items(self):
        QuestionItem.objects.filter(question=self.instance).delete()

    def update(self):
        if self.data.get('question_item'):
            self._delete_all_question_items()
            self._create_question_item(self.instance, self.data.get('question_item'))
            del self.data['question_item']

        for key in self.data.keys():
            setattr(self.instance, key, self.data[key])
        self.instance.save()
        return self.instance
