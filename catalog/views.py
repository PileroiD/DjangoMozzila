from django.shortcuts import render
from django.views import generic
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm


def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """
    # Генерация "количеств" некоторых главных объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Доступный книги(статус = "а")
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()
    # Метод 'all()' применен по умолчанию.
    num_authors = Author.objects.count()

    num_genre = Genre.objects.all().count()

    num_authors = Author.objects.count()
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
        'num_genre': num_genre,
    }

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(request, 'index.html', context=context)


# ------------------------------------------------------------------------------------------------------------------------
class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    # ваше собственное имя переменной контекста в шаблоне
    context_object_name = 'my_book_list'
    # Определение имени вашего шаблона и его расположения
    template_name = 'books/my_arbitrary_template_name_list.html'

    def get_queryset(self):
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        # В первую очередь получаем базовую реализацию контекста
        context = super(BookListView, self).get_context_data(**kwargs)
        return context


# ------------------------------------------------------------------------------------------------------------------------
class BookDetailView(generic.DetailView):
    model = Book


# ------------------------------------------------------------------------------------------------------------------------
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
    context_object_name = 'my_author_list'
    template_name = 'authors/my_arbitrary_template_name_list.html'

    def get_queryset(self):
        return Author.objects.all()

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        return context


# ------------------------------------------------------------------------------------------------------------------------
class AuthorDetailView(generic.DetailView):
    model = Author


# ------------------------------------------------------------------------------------------------------------------------
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


# ------------------------------------------------------------------------------------------------------------------------
class LoanedBooksByAllUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    context_object_name = 'my_all_borrow'
    template_name = 'catalog/bookinstance_list_borrowed_user_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.all().order_by('due_back')


# ------------------------------------------------------------------------------------------------------------------------
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('books'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date, })

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})


# ------------------------------------------------------------------------------------------------------------------------
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


# ------------------------------------------------------------------------------------------------------------------------
from .models import Book

class BookCreate(CreateView):
    model = Book
    fields = '__all__'

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
