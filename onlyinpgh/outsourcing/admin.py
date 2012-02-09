from django.contrib import admin
from onlyinpgh.outsourcing.models import FacebookPage, FacebookOrgRecord, FacebookEventRecord, ExternalPlaceSource

admin.site.register(FacebookPage)
admin.site.register(FacebookOrgRecord)
admin.site.register(FacebookEventRecord)
admin.site.register(ExternalPlaceSource)
