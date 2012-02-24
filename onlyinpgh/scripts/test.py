from places.models import Place
from places.views import FeedItem as PlaceFeedItem
from events.models import Event
from events.views import FeedItem as EventFeedItem

from django.contrib.auth.models import User

from django.template.loader import get_template
from django.template import Context

# def run():
# 	p = Place.objects.all()[0]
# 	admin = User.objects.get(username='admin')

# 	item = PlaceFeedItem(p,admin)
# 	print item.render_template()

def run():
	admin = User.objects.get(username='admin')
	feed_template = get_template('feed.html')

	place_items_html = []
	for p in Place.objects.all()[:3]:
		item = PlaceFeedItem(p,admin)
		place_items_html.append(item.render_template())
	page_html = feed_template.render(Context({'items':place_items_html,'class_name':'places-feed'}))

	event_items_html = []
	for e in Event.objects.all()[:3]:
		item = EventFeedItem(e)
		event_items_html.append(item.render_template())
	page_html += feed_template.render(Context({'items':event_items_html,'class_name':'events-feed'}))

	print page_html