from django.db import models


TYPE_ANSWER = (
    ('answer_text', 'Ответ текстом'),
    ('answer_one_selected', 'Ответ с выбором одного варианта'),
    ('answer_some_selected', 'Ответ с выбором нескольких вариантов'),
)


class Quiz(models.Model):
    """Модель содержащая опросы"""
    name = models.CharField(max_length=256, verbose_name='Название')
    start_date = models.DateTimeField(verbose_name='Дата старта')
    finish_date = models.DateTimeField(verbose_name='Дата окончания')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.name


class Question(models.Model):
    """Вопросы для опроса"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='Опрос')
    text = models.TextField(verbose_name='Текст вопроса')
    type = models.CharField(choices=TYPE_ANSWER, max_length=256, verbose_name='Тип вопроса')

    def __str__(self):
        return f"{self.quiz}|{self.text}"


class QuestionItem(models.Model):
    """Ответы на вопрос с возможностью их выбора"""
    name = models.CharField(max_length=256, verbose_name='Вариант ответа')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_items', verbose_name='Ответ с выбором')

    def __str__(self):
        return self.name


class User(models.Model):
    """Пользователь"""
    name = models.CharField(max_length=256, unique=True, verbose_name='Имя пользователя')

    def __str__(self):
        return self.name


class Answer(models.Model):
    """Ответы на вопросы"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Ответ на вопрос', blank=True, null=True)
    question = models.ForeignKey(Question, models.CASCADE, verbose_name='Вопрос')
    answer_selected = models.ManyToManyField(
        QuestionItem, verbose_name='Ответы/Ответ на вопрос выбранные из списка ответов', blank=True
    )

    def __str__(self):
        return f"{self.question}| {self.text}"