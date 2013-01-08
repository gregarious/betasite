# Future work #

- Tagged comments with "FUTURE" that deal with some good ideas for enhancing/refactoring features.
- Consider replacing sorl Thumbnails with easy-thumbnails. More active development and I think I like its style a bit better. One issue though: I don't know if it supports easy deletion of all orphaned thumbs?

# Configuration #

**TODO**

# Stack/admin notes #

## Non-python dependencies ##

- PostgreSQL
- RabbitMQ Server
- Elasticsearch (see extended notes in Third-party Package notes section)
- yuicompressor (wrote custom yuicompressor script that handles calling the included jar file)

## supervisor processes ##

[supervisor](http://supervisord.org/configuration.html) is recommended for out-of-the-box process running. Included in `/etc/supervisord/` are sample conf files for the following processes:
- celeryd (standard celery worker)
- celerybeat (handles cron-like periodic tasks)
- elasticsearch (search engine service)

## Static files ##

Static file serving is not part of this install. The /static/ and /media/ endpoints must be supported externally (a separate nginx Webfaction app in the case of the current production server).

## virtualenv ##

## cron jobs ##

Recommended cron jobs:
- Database backup

# Third-party Package Notes #

## Haystack ##

Using v2.0.0-beta since I assumed it would be released sometime soon after I started playing around with it, but 8 months later it's still in beta.

Really good ideas in Haystack: modeling after the ORM, search index templates, focus on indexing models, but the project looks to be a little too lofty to pull it all off in a stable way. Documentation is very complete on some subjects, absent on others. Lots of cool advanced features: spatial search, querysets that filter on a attributes that are stored in the index, etc, but I ran into a few bugs here and there on some fairly basic tasks (submitted a ticket even).

But as it turns out, querying all heterogenous items via a QuerySet-like interface might not be a great idea. Filtering by stored fields is screwy.  Since not all indexed models have the same filterable field name, it'll just leaves out all results for models that don't have the filterable field. Also it's buggy (e.g. dtend=datetime.now() will crash, dtend__lte=datetime.now() won't)

Don't want to spend the effort of implementing a new search backend, so going to stick with Haystack and just take advantage of it for index template and tight integration of search results to model types.

A few reminders for things that either aren't documented or are hard to find in Haystack's docs:
- All indexed dates/times are stored as naive datetimes in UTC. Not sure if this is a Haystack decision or up to the search backend.

## Elasticsearch ##

The current install uses Elasticsearch as the search backend. The whole Elasticsearch package is self-contained in the project's `opt/elasticsearch/` directory.

For the most part, the library can be updated by simply replacing the directory wholesale. The one exception is the configuration changes that make the project play well with the self-contained var directory. These are documented in `opt/elasticsearch/config/README.txt`, so **this documentation will be overwritten when the install is replaced.** Be sure to keep a copy around for reference when upgrading the install (and remember to add the README into the new install, too).

A Java Service Wrapper was used previously to manage the service (see any previous v1.0 commit), but was rendered obsolete by the introduction of supervisor. This could be useful again if we see some specific problems (e.g. [this issue](http://www.elasticsearch.org/tutorials/2011/04/06/too-many-open-files.html)), but it's doubtful.

## Celery ##

Although the Django admin plugin to monitor Celery processes was pretty simple ([see this post on stackoverflow for info on how to set it back up](http://stackoverflow.com/questions/10660202/how-do-i-set-a-backend-for-django-celery-i-set-celery-result-backend-but-it-is)), it's probably overkill, requires even more daemon features to be running (celerycam, -E flag for worker), and isn't officially recommended by the Celery folks anymore. As a result, Flower is in place now. It's a pretty nice tool, but it's fairly early in development and isn't well documented yet. I can't find a simple way to access it's data on a remote webserver, or to store task history persistently. No big deal, but might want to keep an eye on the project, and look into these things if monitoring async tasks becomes more than just a curiousity.
