from django.contrib import admin

from quiz.models import Quiz, Question, QuestionItem, Answer, User

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'text']

# admin.site.register(Answer)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuestionItem)
admin.site.register(User)
