from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('manualmove/', views.myManualViewView, name='manual-move'),
    path('automaticmove/', views.myAutomaticViewView, name='automatic-move'),
    
    #path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    #path('authors/', views.AuthorListView.as_view(), name='authorsLOP'),
    #path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    #path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]
