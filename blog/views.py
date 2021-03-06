from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm




# # Function Based view
def post_list(request, tag_slug = None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 2) # 2 Posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except  PageNotAnInteger:
        # If page is not an integer, just give the firstpage
        posts = paginator.page(1)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})
 
#  # Class based view
# class PostListView(ListView):
#     queryset = Post.published.all()

#     # Default context variable name is object_list
#     context_object_name = 'posts'
#     paginate_by = 2
#     template_name = 'blog/post/list.html'

#     # This sends the page object for pagination with the name 'page_obj'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
    status='published',
    publish__year=year,
    publish__month=month,
    publish__day=day)

    # List similiar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similiar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similiar_posts = similiar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    comments = post.comments.all().filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()

    comment_form = CommentForm()

    return render(request, 'blog/post/detail.html', {'post': post, 'comments':comments, 'new_comment':new_comment, 'comment_form':comment_form, 'similiar_posts':similiar_posts})

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

def post_search(request):
    form = SearchForm()
    query = None
    results = None
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # Weighted Queries
            # search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            # search_query = SearchQuery(query)
            # results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')

            # Trigram similarity
            results = Post.published.annotate(similarity=TrigramSimilarity('title', query)).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})