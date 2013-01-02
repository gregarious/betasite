Note configuration changes made for Scenable project config
(mostly settings to use local var/ directory):

config/elasticsearch.yml:
- adjusted path.data and path.logs values to "../../var/index" and
    "../../var/log", respectively

bin/service/elasticsearch:
- replaced script's PIDDIR value to "../../../../var/run/elasticsearch"

bin/service/elasticsearch.conf:
- changed wrapper.logfile value to "%ES_HOME%/../../var/log/elasticsearch-service.log"