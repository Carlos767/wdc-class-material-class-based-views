from datetime import datetime

from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, RedirectView
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Author, Book
from .forms import BookForm, SignUpForm


def is_staff(user):
    return user.is_staff


class IndexView(TemplateView):
    template_name = 'books.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.all()
        sort_method = self.request.GET.get('sort', 'asc')
        if sort_method == 'asc':
            books = books.order_by('popularity')
        elif sort_method == 'desc':
            books = books.order_by('-popularity')

        if 'q' in self.request.GET:
            q = self.request.GET['q']
            books = books.filter(title__icontains=q)

        context['books'] = books
        context['authors'] = Author.objects.all()
        context['sort_method'] = sort_method
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # initialize list of favorite books for current session
        request.session.setdefault('favorite_books', [])
        request.session.save()

        return self.render_to_response(context)


class BooksView(RedirectView):
    url = '/'


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_staff), name='dispatch')
class CreateBookView(CreateView):
    model = Book
    fields = ['title', 'author', 'isbn', 'popularity']
    template_name = 'create_book.html'
    success_url = '/'


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_staff), name='dispatch')
class EditBookView(UpdateView):
    model = Book
    fields = ['title', 'author', 'isbn', 'popularity']
    template_name = 'edit_book.html'
    success_url = '/'


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_staff), name='dispatch')
class DeleteBookView(DeleteView):
    model = Book
    success_url = '/'


class AuthorsView(ListView):
    model = Author
    template_name = 'authors.html'


class AuthorView(DetailView):
    model = Author
    template_name = 'author.html'


class FavoritesView(TemplateView):
    template_name = 'favorites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books_ids = self.request.session.get('favorite_books', [])
        favorite_books = Book.objects.filter(id__in=books_ids)
        context['favorite_books'] = favorite_books
        return context


class AddFavorite(View):

    def post(self, request, *args, **kwargs):
        request.session.setdefault('favorite_books', [])
        request.session['favorite_books'].append(request.POST.get('book_id'))
        request.session.save()
        return redirect('index')


class RemoveFavorite(View):

    def post(self, request, *args, **kwargs):
        if request.session.get('favorite_books'):
            request.session['favorite_books'].remove(request.POST.get('book_id'))
            request.session.save()
        return redirect('index')


class SignUpView(TemplateView):
    template_name = 'signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = SignUpForm()
        return context

    def post(self, request, *args, **kwargs):
        signup_form = SignUpForm(request.POST)
        if signup_form.is_valid():
            user = User.objects.create(username=request.POST['username'])
            user.set_password(request.POST['password'])
            user.save()
            login(request, user)
            return redirect('index')
        return render(
            request,
            'signup.html',
            context={'signup_form': signup_form}
        )
