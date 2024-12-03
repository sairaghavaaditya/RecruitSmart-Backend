from django.contrib import admin
from .models import Question, UsersResponses

admin.site.register(Question)
admin.site.register(UsersResponses)
