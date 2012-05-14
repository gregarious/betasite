from django.shortcuts import render_to_response
from scenable.common.views import PageContext
from scenable.chatter.models import Post
from scenable.chatter.forms import PostForm
from django.contrib.auth.decorators import login_required


@login_required
def page_feed(request):
    if request.POST:
        submit_form = PostForm(author=request.user, data=request.POST)
        if submit_form.is_valid():
            if submit_form.cleaned_data['content'].strip() != '':
                submit_form.save()
            # create new form -- don't want the post text in there again
            submit_form = PostForm(author=request.user)
    else:
        submit_form = PostForm(author=request.user)

    items = Post.objects.all().order_by('-dtcreated')
    context = PageContext(request,
        current_section='chatter',
        page_title='Scenable | Chatter Feed',
        content_dict={'items': items, 'form': submit_form})
    return render_to_response('chatter/page_feed.html', context_instance=context)
