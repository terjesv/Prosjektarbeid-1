from itertools import chain
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from cms.forms import PostForm, ReviewForm, SubscriptionForm, AssignForm
from cms.models import Post, Category, Review, Subscription
from cms.templatetags.auth_extras import has_group


class PostListView(ListView):
    context_object_name = 'posts'
    queryset = Post.objects.filter(published=True)

    def get_context_data(self, *, object_list=queryset, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class DraftListView(PermissionRequiredMixin, PostListView):
    queryset = Post.objects.filter(published=False)
    template_name = 'cms/post_list.html'
    permission_required = 'cms.change_post'


class SavedPostListView(PostListView):
    context_object_name = 'posts'
    template_name = 'cms/post_list.html'

    def get_queryset(self):
        return Post.objects.filter(saved_by_users__username=self.request.user.username)


class PostCreateView(PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = '/drafts'
    permission_required = 'cms.add_post'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        post.authors.set(form.cleaned_data['authors'])
        post.categories.set(form.cleaned_data['categories'])
        post.authors.add(self.request.user)
        post.save()
        return HttpResponseRedirect(reverse('post_detail', kwargs={'pk': post.pk}))


class CategoryCreateView(PermissionRequiredMixin, CreateView):
    model = Category
    fields = ('name',)
    success_url = '/add_category'
    permission_required = 'cms.add_category'
    template_name = "cms/category_create.html"


class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user in self.get_object().authors.all()


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostCreateView.form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        post = form.save(commit=False)
        if 'author' in self.request.user.groups.all():
            post.authors.add(self.request.user)
        post.authors.set(form.cleaned_data['authors'])
        post.categories.set(form.cleaned_data['categories'])
        post.save()
        return HttpResponseRedirect(reverse('post_detail', kwargs={'pk': post.pk}))

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        user = self.request.user
        return user.is_superuser or user in chain(post.authors.all(), post.assigned_users.all())


class PostDetailView(UserPassesTestMixin, DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['review_form'] = ReviewForm
        context['assign_form'] = AssignForm
        return context

    def test_func(self):
        post = self.get_object()
        return post.published or self.request.user.has_perm('cms.change_post')


class SubscriptionListView(LoginRequiredMixin, PostListView):
    template_name = 'cms/subscriptions.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            request.user.subscription
        except AttributeError:
            if request.user.is_authenticated:
                request.user.subscription = Subscription.objects.create(owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        sub = self.request.user.subscription
        by_category = Post.objects.filter(categories__in=sub.categories.all()).exclude(published=False)
        by_author = Post.objects.filter(authors__in=sub.authors.all()).exclude(published=False)
        return sorted(chain(by_category, by_author), key=(lambda p: p.id))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SubscriptionForm()
        context['subscription_page'] = True
        return context


########################################################
########################################################


def publish_post_view(request, pk):
    if request.method == 'POST':
        if request.user.has_perm('cms.publish_post'):
            post = Post.objects.get(pk=pk)
            if post.published:
                post.published = False
                post.save()
                return HttpResponseRedirect(reverse('draft_list'))
            else:
                post.published = True
                post.save()
            return HttpResponseRedirect(reverse('post_list'))
        raise PermissionDenied("only editors can publish posts")


def save_post_to_user_view(request, pk):
    if request.method == 'POST':
        if request.user.is_authenticated:
            post = Post.objects.get(pk=pk)
            if post.saved_by_users.filter(username=request.user.username).exists():
                post.saved_by_users.remove(request.user)
            else:
                post.saved_by_users.add(request.user)
            post.save()
            return HttpResponseRedirect(reverse('post_detail', kwargs={'pk': post.pk}))
        raise PermissionDenied("Only logged in users can save posts")


def assign_post_view(request, pk):
    if request.method == 'POST':
        if request.user.has_perm("cms.add_review"):
            post = Post.objects.get(pk=pk)
            if post.assigned_users.filter(pk=request.user.pk).exists():
                post.assigned_users.remove(request.user)
            else:
                post.assigned_users.add(request.user)
            post.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', None))
        raise PermissionDenied("Only editors can review posts")


def add_review_view(request, pk):
    if request.user.has_perm("cms.add_review"):
        post = Post.objects.get(pk=pk)
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.post = post
                review.editor = request.user
                review.save()
                post.reviews.add(review)
                post.save()
                return HttpResponseRedirect(reverse('post_detail', kwargs={'pk': post.pk}))
    raise PermissionDenied("Only editors can review posts")


def delete_review_view(request, pk):
    if request.method == 'POST':
        if request.user == Review.objects.get(pk=pk).editor or request.user.has_perm("cms.delete_review"):
            Review.objects.filter(pk=pk).delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', None))
        raise PermissionDenied("Only admins can delete the reviews of other users")


def update_subscriptions(request, pk):
    if request.user.is_authenticated and request.method == 'POST':
        subscription = get_object_or_404(Subscription, pk=pk)
        form = SubscriptionForm(request.POST)
        if not request.user == subscription.owner:
            raise PermissionDenied("You cannot set other people's permissions")
        if form.is_valid():
            subscription.authors.set(form.cleaned_data['authors'])
            subscription.categories.set(form.cleaned_data['categories'])
            return HttpResponseRedirect(reverse_lazy('subscriptions'))
    raise PermissionDenied("Permission missing")


def assign_editor_view(request, pk):
    if request.method == 'POST':
        if not request.user.has_perm('cms.assign_editors'):
            raise PermissionDenied("Only editors can edit posts")
        editor_ids = [request.POST['editors']]
        post = Post.objects.get(pk=pk)
        for editor_id in editor_ids:
            editor = User.objects.get(pk=editor_id)
            post.assigned_users.add(editor)
        return HttpResponseRedirect('/{}'.format(pk))


def content_status_view(request, pk):
    if request.method == 'POST':
        if request.user.has_perm("cms.change_post"):
            post = Post.objects.get(pk=pk)
            if post.complete:
                post.complete = False
            else:
                post.complete = True
            post.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', None))
    raise PermissionDenied("Only editors can mark content as complete")

