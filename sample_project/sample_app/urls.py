from django.urls import path
from django.conf.urls import include

from . import views


urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),

    path('', views.IndexView.as_view(), name='index'),
    path('authors/', views.AuthorsView.as_view(), name='authors'),
    path('author/<int:pk>/', views.AuthorView.as_view(), name='author_by_id'),
    path('create_book/', views.CreateBookView.as_view(), name='create_book'),
    path('edit_book/<int:book_id>/', views.EditBookView.as_view(), name='edit_book'),
    path('delete_book', views.DeleteBookView.as_view(), name='delete_book'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('add-to-favorites/', views.AddFavorite.as_view(), name='add_to_favorites'),
    path('remove-from-favorites/', views.RemoveFavorite.as_view(), name='remove_from_favorites'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('books/', views.BooksView.as_view(), name='books'),
]
