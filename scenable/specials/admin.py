from django.contrib import admin
from scenable.specials.models import Special, Coupon


class CouponAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)

admin.site.register(Special)
admin.site.register(Coupon, CouponAdmin)