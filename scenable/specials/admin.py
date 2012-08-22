from django.contrib import admin
from scenable.specials.models import Special, Coupon


class CouponAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)


class SpecialAdmin(admin.ModelAdmin):
    list_display = ('title', 'place', 'dexpires', 'id')

admin.site.register(Special, SpecialAdmin)
admin.site.register(Coupon, CouponAdmin)
