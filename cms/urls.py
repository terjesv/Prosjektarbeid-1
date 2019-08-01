from django.urls import path
from cms.populate import populate
from cms.views import PostListView, DraftListView, publish_post_view, PostCreateView, PostUpdateView, \
    save_post_to_user_view, \
    SavedPostListView, assign_post_view, add_review_view, delete_review_view, PostDetailView, SubscriptionListView, \
    update_subscriptions, assign_editor_view, PostDeleteView, CategoryCreateView, content_status_view

urlpatterns = [
    path('', PostListView.as_view(), name="post_list"),
    path('drafts', DraftListView.as_view(), name="draft_list"),
    path('new', PostCreateView.as_view(), name="post_form"),
    path('saved', SavedPostListView.as_view(), name="saved_posts"),
    path('subscriptions', SubscriptionListView.as_view(), name="subscriptions"),
    path('subscriptions/<int:pk>/update', update_subscriptions, name='update_subscription'),

    path('<int:pk>/publish', publish_post_view, name="publish_post"),
    path('<int:pk>/edit', PostUpdateView.as_view(), name="post_update"),
    path('<int:pk>/save', save_post_to_user_view, name='save_post'),
    path('<int:pk>/assign', assign_post_view, name="assign_post"),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name="delete_post"),
    path('<int:pk>/status', content_status_view, name="content_status"),
    path('<int:pk>/add_review', add_review_view, name="add_review"),
    path('<int:pk>/delete_review', delete_review_view, name="delete_review"),
    path('add_category', CategoryCreateView.as_view(), name="create_category"),
    path('<int:pk>/assign_editor', assign_editor_view, name="assign_editor"),
    path('<int:pk>', PostDetailView.as_view(), name="post_detail"),

    path('populate', populate, name="populate"),
]
