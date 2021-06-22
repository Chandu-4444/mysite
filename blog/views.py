from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 2) # 2 Posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except  PageNotAnInteger:
        # If page is not an integer, just give the firstpage
        posts = paginator.page(1)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
    status='published',
    publish__year=year,
    publish__month=month,
    publish__day=day)

    return render(request, 'blog/post/detail.html', {'post': post})

