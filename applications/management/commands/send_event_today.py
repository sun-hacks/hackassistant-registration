from datetime import timedelta

from django.core import mail
from django.core.management.base import BaseCommand
from django.utils import timezone


from applications import models, emails


class Command(BaseCommand):
    help = 'Sends event today blast'

    def handle(self, *args, **options):
        confirmed = models.Application.objects.filter(status=models.APP_CONFIRMED)
        wait_list = models.Application.objects.filter(status=models.APP_REJECTED)
        all_attendees = confirmed | wait_list
        self.stdout.write('Checking all attendees...%s found' % all_attendees.count())
        self.stdout.write('Sending todays email...')
        msgs = []
        for app in all_attendees:
            app.send_info()
            msgs.append(emails.create_event_today_email(app))
        connection = mail.get_connection()
        connection.send_messages(msgs)
        self.stdout.write(self.style.SUCCESS(
            'Sending hypes... Successfully sent %s hypes' % len(msgs)))
