from datetime import datetime

from django.views.generic import View
from django.urls import reverse
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator

from .models import Author, Book
from .forms import BookForm, SignUpForm


def is_staff(user):
    return user.is_staff


class IndexView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        books = Book.objects.all()
        sort_method = request.GET.get('sort', 'asc')
        if sort_method == 'asc':
            books = books.order_by('popularity')
        elif sort_method == 'desc':
            books = books.order_by('-popularity')

        if 'q' in request.GET:
            q = request.GET['q']
            books = books.filter(title__icontains=q)

        # initialize list of favorite books for current session
        request.session.setdefault('favorite_books', [])
        request.session.save()

        context['books'] = books
        context['authors'] = Author.objects.all()
        context['sort_method'] = sort_method

        return render(request, 'books.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_staff), name='dispatch')
class CreateBookView(View):

    def get(self, request, *args, **kwargs):
        book_form = BookForm()
        return render(
            request,
            'create_book.html',
            context={'book_form': book_form}
        )

    def post(self, request, *args, **kwargs):
        book_form = BookForm(request.POST)
        if book_form.is_valid():
            book_form.save()
            return redirect('index')
        return render(
            request,
            'create_book.html',
            context={'book_form': book_form}
        )


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_staff), name='dispatch')
class EditBookView(View):

    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=kwargs.get('book_id'))
        book_form = BookForm(instance=book)
        return render(
            request,
            'edit_book.html',
            context={
                'book': book,
                'book_form': book_form
            }
        )

    def post(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=kwargs.get('book_id'))
        book_form = BookForm(request.POST, instance=book)
        if book_form.is_valid():
            book_form.save()
            return redirect('index')
        return render(
            request,
            'edit_book.html',
            context={
                'book': book,
                'book_form': book_form
            }
        )


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_staff), name='dispatch')
class DeleteBookView(View):

    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        book.delete()
        return redirect('/')


class AuthorsView(View):

    def get(self, request, *args, **kwargs):
        authors = Author.objects.all()
        return render(request, 'authors.html', {
            'authors': authors
        })


class AuthorView(View):

    def get(self, request, *args, **kwargs):
        author = get_object_or_404(Author, id=kwargs.get('author_id'))
        return render(request, 'author.html', {
            'author': author
        })


class FavoritesView(View):

    def get(self, request, *args, **kwargs):
        books_ids = request.session.get('favorite_books', [])
        favorite_books = Book.objects.filter(id__in=books_ids)
        return render(
            request,
            'favorites.html',
            context={
                'favorite_books': favorite_books,
            }
        )


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


class SignUpView(View):

    def get(self, request, *args, **kwargs):
        signup_form = SignUpForm()
        return render(
            request,
            'signup.html',
            context={'signup_form': signup_form}
        )

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
