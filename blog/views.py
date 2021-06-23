from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail



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

    comments = Comment.objects.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()


    return render(request, 'blog/post/detail.html', {'post': post, 'comments':comments, 'new_comment':new_comment, 'comment_form':comment_form})

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url()) # build_absolute_uri() attaches the full url, http://127.0.0.1:8000.....
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}'s comments :{cd['comment']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
        
    return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent': sent})
