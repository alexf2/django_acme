# from django.shortcuts import render
from typing import Any
from django.views.generic import TemplateView

from birthday.models import Birthday

'''
def homepage(request):
    return render(request, 'pages/index.html')
'''


class HomePage(TemplateView):
    # В атрибуте template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница.
    template_name = 'pages/index.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['total_count'] = Birthday.objects.count()
        return context
