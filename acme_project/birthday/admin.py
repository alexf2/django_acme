from .models import Tag
from django.contrib import admin

admin.site.empty_value_display = 'Не задано'


admin.site.register(Tag)
