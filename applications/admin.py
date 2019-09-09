from django.conf import settings
from django.contrib import admin
# Register your models here.
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince

from applications import models

import csv
from django.http import HttpResponse

EXPORT_CSV_FIELDS = ['name', 'email', 'phone_number', 'university', 'gender','other_gender','ethnicity','other_ethnicity','degree', 'education', 'graduation_year', 'referral']

EXPORT_CSV_FOR_SENDY = ['name','email']


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'votes', 'reimb', 'status',
                    'status_last_updated', 'diet')
    list_filter = ('status', 'first_timer', 'reimb', 'graduation_year',
                   'university', 'origin', 'under_age', 'diet')
    list_per_page = 200
    search_fields = ('user__name', 'user__email',
                     'description',)
    ordering = ('submission_date',)
    date_hierarchy = 'submission_date'

    actions = ["export_as_sendy","export_as_csv"]
    def export_as_sendy(self, request, queryset):
        meta = self.model._meta

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(EXPORT_CSV_FOR_SENDY)
        for obj in queryset:
            row = []
            for field in EXPORT_CSV_FOR_SENDY:
                if hasattr(getattr(obj,'user'),field):
                    row.append(getattr(getattr(obj,'user'),field))
                else:
                    row.append(getattr(obj,field))
            written = writer.writerow(row)

        return response
    export_as_sendy.short_description = "Export to Sendy CSV"

    def export_as_csv(self, request, queryset):
        meta = self.model._meta

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(EXPORT_CSV_FIELDS)
        for obj in queryset:
            row = []
            for field in EXPORT_CSV_FIELDS:
                if hasattr(getattr(obj,'user'),field):
                    row.append(getattr(getattr(obj,'user'),field))
                else:
                    row.append(getattr(obj,field))
            written = writer.writerow(row)
        return response
    export_as_csv.short_description = "Export to CSV"

    def name(self, obj):
        return obj.user.get_full_name() + ' (' + obj.user.email + ')'

    name.admin_order_field = 'user__name'  # Allows column order sorting
    name.short_description = 'Hacker info'  # Renames column head

    def votes(self, app):
        return app.vote_avg

    votes.admin_order_field = 'vote_avg'

    def status_last_updated(self, app):
        if not app.status_update_date:
            return None
        return timesince(app.status_update_date)

    status_last_updated.admin_order_field = 'status_update_date'

    def get_queryset(self, request):
        qs = super(ApplicationAdmin, self).get_queryset(request)
        return models.Application.annotate_vote(qs)


admin.site.register(models.Application, admin_class=ApplicationAdmin)
admin.site.site_header = '%s Admin' % settings.HACKATHON_NAME
admin.site.site_title = '%s Admin' % settings.HACKATHON_NAME
admin.site.index_title = 'Home'
admin.site.login = login_required(admin.site.login)
