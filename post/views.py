from django.shortcuts import render
from .models import Post
from django.shortcuts import HttpResponseRedirect
from .forms import NewCommentForm, PostSearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from taggit.models import Tag
from django.shortcuts import render
from django.template.loader import render_to_string
from blog.meta_gen import meta_keywords

this_template = "base.html"


def tabs(request):
    return render (this_template,
                              {'title': "Page Name", 'keys': meta_keywords(render_to_string(this_template))})


# Create your views here.


class PostListView(ListView):
    model = Post
    template_name = 'blog.html'
    context_object_name = 'posts'
    ordering = ['-publish']
    paginate_by = 4
    queryset = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        common_tags = Post.tags.most_common()[:4]
        most_recent = Post.objects.order_by('-publish')[:5]
        context['most_recent'] = most_recent
        context['common_tags'] = common_tags
        return context


def tagged(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = Post.tags.most_common()[:4]
    posts = Post.objects.filter(tags=tag)
    context = {
        'tag': tag,
        'common_tags': common_tags,
        'posts': posts,
    }
    return render(request, 'blog.html', context)


# def post_detail(request, id):
#   post = get_object_or_404(Post, id=id)
#  form = CommentForm(request.POST or None)
# if request.method == "POST":
#    if form.is_valid():
#       form.instance.user = request.user
#      form.instance.post = post
##    return redirect('post_detail', kwargs={
#       'id': post_detail.id
#  })
# context = {
#    'form': form,
#   'post': post,
# }
# return render(request, 'post_detail.html', context)


def post_detail(request, post):
    post = get_object_or_404(Post, slug=post, status='published')
    allcomments = post.comments.filter(status=True)
    page = request.GET.get('page', 1)

    paginator = Paginator(allcomments, 10)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    user_comment = None

    if request.method == 'POST':
        comment_form = NewCommentForm(request.POST)
        if comment_form.is_valid():
            user_comment = comment_form.save(commit=False)
            user_comment.post = post
            user_comment.save()
            return HttpResponseRedirect('/' + post.slug)
    else:
        comment_form = NewCommentForm()
    return render(request, 'post_detail.html',
                  {'post': post, 'comments': user_comment, 'comments': comments, 'comment_form': comment_form,
                   'allcomments': allcomments, })


def post_search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query) |
            Q(thumbnail__icontains=query)
        ).distinct()
    context = {
        'queryset': queryset
    }
    return render(request, 'search.html', context)
