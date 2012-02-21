from django.shortcuts import render_to_response
from onlyinpgh.tags.models import Tag

def detail_page(request,tid):
    return render_to_response('tags/tag-details.html',{'tag':Tag.objects.get(id=tid)})

def all_tags(request):
	variables = { 'tags': Tag.objects.all() }
	return render_to_response('tags.html', variables)