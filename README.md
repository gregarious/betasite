# Future work #

- Tagged comments with "FUTURE" that deal with some good ideas for enhancing/refactoring features.

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

Really good ideas in Haystack: modeling after the ORM, search index templates, focus on indexing models, but the project looks to be a little too lofty to pull it all off in a stable way. Documentation is very complete on some subjects, absent on others. Lots of cool advanced features: spatial search, querysets that filter on a attributes that aren't directly indexed, etc, but I ran into a few bugs here and there on some fairly basic tasks (submitted a ticket even).

Given that, and how much if a rabbit hole debugging the Haystack core can be, I think it's best to keep it super simple and use the minimum number of extras. Basically, just sticking with taking advantage of the template indices and tight integration of search results to model types.

## Elasticsearch ##

The current install uses Elasticsearch as the search backend. The whole Elasticsearch package is self-contained in the project's `opt/elasticsearch/` directory.

A few configuration changes were done to make the project play well with the self-contained var directory, and these are documented in `opt/elasticsearch-x.y.z/config/README.txt`. **Note that this README will overwritten if the install is replaced.** Be sure to keep a copy around when messing with the install.

A Java Service Wrapper was used previously to manage the service (see any previous v1.0 commit), but was rendered obsolete by the introduction of supervisor. This could be useful again if we see some specific problems (e.g. [this issue](http://www.elasticsearch.org/tutorials/2011/04/06/too-many-open-files.html)), but it's doubtful.