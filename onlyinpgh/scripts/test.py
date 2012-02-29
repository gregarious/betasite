from places.models import Place
from places.viewmodels import PlacesFeed, PlaceFeedItem

# def run():
# 	p = Place.objects.all()[0]
# 	admin = User.objects.get(username='admin')

# 	item = PlaceFeedItem(p,admin)
# 	print item.render_template()

def run():
	item = PlaceFeedItem(Place.objects.all()[1])
	#print item.to_json()

	feed = PlacesFeed.init_from_places(Place.objects.all()[:10])
	print feed.to_html()
	#print feed.to_json()
