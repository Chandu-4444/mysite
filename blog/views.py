from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView


# # Function Based view
# def post_list(request):
#     object_list = Post.published.all()
#     paginator = Paginator(object_list, 2) # 2 Posts per page
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except  PageNotAnInteger:
#         # If page is not an integer, just give the firstpage
#         posts = paginator.page(1)
#     return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})
 
 # Class based view
class PostListView(ListView):
    queryset = Post.published.all()

    # Default context variable name is object_list
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list.html'

    # This sends the page object for pagination with the name 'page_obj'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
    status='published',
    publish__year=year,
    publish__month=month,
    publish__day=day)

    return render(request, 'blog/post/detail.html', {'post': post})


