from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from .forms import BirthdayForm, CongratulationForm
from .models import Birthday, Congratulation
from .utils import calculate_birthday_countdown

# Создаём миксин.

# CBV: https://ccbv.co.uk/projects/Django/3.2/
#   https://docs.djangoproject.com/en/3.2/ref/class-based-views/


class BirthdayMixin:
    model = Birthday
    success_url = reverse_lazy('birthday:list')


class BirthdayFormMixin:
    form_class = BirthdayForm
    # template_name = 'birthday/birthday.html'


'''
def birthday(request, pk=None):
    # Если в запросе указан pk (если получен запрос на редактирование объекта):
    if pk is not None:
        # Получаем объект модели или выбрасываем 404 ошибку.
        instance = get_object_or_404(Birthday, pk=pk)
    # Если в запросе не указан pk
    # (если получен запрос к странице создания записи):
    else:
        # Связывать форму с объектом не нужно, установим значение None.
        instance = None
    # Передаём в форму либо данные из запроса, либо None.
    # В случае редактирования прикрепляем объект модели.
    form = BirthdayForm(request.POST or None,
                        files=request.FILES or None,
                        instance=instance)
    # Остальной код без изменений.
    context = {'form': form}
    # Сохраняем данные, полученные из формы, и отправляем ответ:
    if form.is_valid():
        form.save()
        birthday_countdown = calculate_birthday_countdown(
            form.cleaned_data['birthday']
        )
        # добавляем dict в dict
        context.update({'birthday_countdown': birthday_countdown})
    return render(request, 'birthday/birthday_form.html', context)
'''


class BirthdayCreateView(LoginRequiredMixin, CreateView):  # Class-Based Views
    # Указываем модель, с которой работает CBV...
    model = Birthday
    # Этот класс сам может создать форму на основе модели!
    # Нет необходимости отдельно создавать форму через ModelForm.
    # Указываем поля, которые должны быть в форме:
    # fields = '__all__'
    form_class = BirthdayForm  # применим нашу форму вместо дефолтной встроенной в CBV
    # Явным образом указываем шаблон:
    # template_name = 'birthday/birthday.html'
    # Указываем namespace:name страницы, куда будет перенаправлен пользователь
    # после создания объекта:

    # добавили в модели get_absolute_url
    # success_url = reverse_lazy('birthday:list')
    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class BirthdayCreateView2(BirthdayMixin, BirthdayFormMixin, CreateView):  # на миксине
    pass


class BirthdayUpdateView2(UserPassesTestMixin, BirthdayMixin, BirthdayFormMixin, CreateView):
    def test_func(self):
        # Получаем текущий объект.
        object = self.get_object()
        # Метод вернёт True или False.
        # Если пользователь - автор объекта, то тест будет пройден.
        # Если нет, то будет вызвана ошибка 403.
        return not object.author or object.author == self.request.user


class BirthdayUpdateView(UserPassesTestMixin, UpdateView):
    model = Birthday
    form_class = BirthdayForm
    # template_name = 'birthday/birthday_form.html'
    # добавили в модели get_absolute_url
    # success_url = reverse_lazy('birthday:list')

    def test_func(self):
        # Получаем текущий объект.
        object = self.get_object()
        # Метод вернёт True или False.
        # Если пользователь - автор объекта, то тест будет пройден.
        # Если нет, то будет вызвана ошибка 403.
        return not object.author or object.author == self.request.user


def delete_birthday(request, pk):
    # Получаем объект модели или выбрасываем 404 ошибку.
    instance = get_object_or_404(Birthday, pk=pk)
    # В форму передаём только объект модели;
    # передавать в форму параметры запроса не нужно.
    form = BirthdayForm(instance=instance)
    context = {'form': form}
    # Если был получен POST-запрос...
    if request.method == 'POST':
        # ...удаляем объект:
        instance.delete()
        # ...и переадресовываем пользователя на страницу со списком записей.
        return redirect('birthday:list')
    # Если был получен GET-запрос — отображаем форму.
    return render(request, 'birthday/birthday.html', context)


class BirthdayDeleteView(DeleteView):
    model = Birthday
    success_url = reverse_lazy('birthday:list')


class BirthdayDeleteView2(BirthdayMixin, DeleteView):
    pass


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['birthday_countdown'] = calculate_birthday_countdown(
            self.object.birthday
        )
        # Записываем в переменную form пустой объект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        return context


def birthday_list(request):
    # Получаем все объекты модели Birthday из БД.
    birthdays = Birthday.objects.all().order_by('id')
    paginator = Paginator(birthdays, 10)

    # Получаем из запроса значение параметра page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Передаём их в контекст шаблона.
    # context = {'birthdays': birthdays}
    context = {'page_obj': page_obj}
    return render(request, 'birthday/birthday_list.html', context)


class BirthdayListView(ListView):  # Альтернатива birthday_list: CBV вместо функций
    # Указываем модель, с которой работает CBV...
    model = Birthday
    queryset = Birthday.objects.prefetch_related(
        'tags').select_related('author')
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10


'''
def edit_birthday(request, pk):
    # Находим запрошенный объект для редактирования по первичному ключу
    # или возвращаем 404 ошибку, если такого объекта нет.
    instance = get_object_or_404(Birthday, pk=pk)
    # Связываем форму с найденным объектом: передаём его в аргумент instance.
    form = BirthdayForm(request.POST or None, instance=instance)
    # Всё остальное без изменений.
    context = {'form': form}
    # Сохраняем данные, полученные из формы, и отправляем ответ:
    if form.is_valid():
        form.save()
        birthday_countdown = calculate_birthday_countdown(
            form.cleaned_data['birthday']
        )
        context.update({'birthday_countdown': birthday_countdown})
    return render(request, 'birthday/birthday_form.html', context)
'''


@login_required
def add_comment(request, pk):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    birthday = get_object_or_404(Birthday, pk=pk)
    # Функция должна обрабатывать только POST-запросы.
    form = CongratulationForm(request.POST)
    if form.is_valid():
        # Создаём объект поздравления, но не сохраняем его в БД.
        congratulation = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        congratulation.author = request.user
        # В поле birthday передаём объект дня рождения.
        congratulation.birthday = birthday
        # Сохраняем объект в БД.
        congratulation.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('birthday:detail', pk=pk)


# порядок обработки запроса
# https://docs.djangoproject.com/en/3.2/ref/class-based-views/base/#view
# setup()
# dispatch()
# http_method_not_allowed()
# options()

# альтернатива add_comment
'''
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView

from .forms import CongratulationForm
from .models import Birthday, Congratulation

class CongratulationCreateView(LoginRequiredMixin, CreateView):
    birthday = None
    model = Congratulation
    form_class = CongratulationForm

    # Переопределяем dispatch()
    def dispatch(self, request, *args, **kwargs):
        self.birthday = get_object_or_404(Birthday, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.birthday = self.birthday
        return super().form_valid(form)

    # Переопределяем get_success_url()
    def get_success_url(self):
        return reverse('birthday:detail', kwargs={'pk': self.birthday.pk}) 
'''
