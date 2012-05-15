from django.shortcuts import render_to_response
from onlyinpgh.tags.models import Tag
from django.contrib.auth.decorators import login_required


@login_required
def detail_page(request, tid):
    return render_to_response('tags/tag-details.html', {'tag': Tag.objects.get(id=tid)})
