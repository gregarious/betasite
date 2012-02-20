from django.shortcuts import render_to_response
from onlyinpgh.tagging.models import Tag

def detail_page(request,tid):
    return render_to_response('tagging/tag-details.html',{'tag':Tag.objects.get(id=tid)})

def all_tags(request):
	variables = { 'tags': Tag.objects.all() }
	return render_to_response('tags.html', variables)