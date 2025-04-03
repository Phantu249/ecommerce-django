from django.urls import path
from .views import CommentListView, CommentCreateView, CommentDetailView

urlpatterns = [
    path('', CommentListView.as_view(), name='comment-list'),
    path('create', CommentCreateView.as_view(), name='comment-create'),
    path('<int:comment_id>', CommentDetailView.as_view(), name='comment-detail'),
]