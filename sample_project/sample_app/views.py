from datetime import datetime

from django.urls import reverse
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from .models import Author, Book
from .forms import BookForm, SignUpForm


def is_staff(user):
    return user.is_staff


def index(request):
    sort_method = request.GET.get('sort', 'asc')
    books = Book.objects.all()
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

    return render(request, 'books.html', {
        'books': books,
        'authors': Author.objects.all(),
        'sort_method': sort_method,
    })


@login_required
@user_passes_test(is_staff)
def create_book(request):
    if request.method == 'GET':
        book_form = BookForm()
        return render(
            request,
            'create_book.html',
            context={'book_form': book_form}
        )
    elif request.method == 'POST':
        book_form = BookForm(request.POST)
        if book_form.is_valid():
            book_form.save()
            return redirect('index')
        return render(
            request,
            'create_book.html',
            context={'book_form': book_form}
        )


@login_required
@user_passes_test(is_staff)
def edit_book(request, book_id=None):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'GET':
        book_form = BookForm(instance=book)
        return render(
            request,
            'edit_book.html',
            context={
                'book': book,
                'book_form': book_form
            }
        )
    elif request.method == 'POST':
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


@login_required
@user_passes_test(is_staff)
def delete_book(request):
    book_id = request.POST.get('book_id')
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('/')


def authors(request):
    authors = Author.objects.all()
    return render(request, 'authors.html', {
        'authors': authors
    })


def author(request, author_id):
    try:
        author = Author.objects.get(id=author_id)
    except Author.DoesNotExist:
        return HttpResponseNotFound()

    return render(request, 'author.html', {
        'author': author
    })


def favorites(request):
    books_ids = request.session.get('favorite_books', [])
    favorite_books = Book.objects.filter(id__in=books_ids)
    return render(
        request,
        'favorites.html',
        context={
            'favorite_books': favorite_books,
        }
    )


def add_to_favorites(request):
    request.session.setdefault('favorite_books', [])
    request.session['favorite_books'].append(request.POST.get('book_id'))
    request.session.save()
    return redirect('index')


def remove_from_favorites(request):
    if request.session.get('favorite_books'):
        request.session['favorite_books'].remove(request.POST.get('book_id'))
        request.session.save()
    return redirect('index')


def signup(request):
    if request.method == 'GET':
        signup_form = SignUpForm()
        return render(
            request,
            'signup.html',
            context={'signup_form': signup_form}
        )
    elif request.method == 'POST':
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
