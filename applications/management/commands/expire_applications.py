from datetime import timedelta

from django.core import mail
from django.core.management.base import BaseCommand
from django.utils import timezone


from applications import models, emails
from app.settings import HACKATHON_APP_DEADLINE


class Command(BaseCommand):
    help = 'Checks invites that have expired and sends reminders 24 before'

    def handle(self, *args, **options):
        fourteendaysbefore=  HACKATHON_APP_DEADLINE - timedelta(days=14)
        self.stdout.write('Checking for apps too close to deadline...')
        too_soons = models.Application.objects.filter(
            status_update_date__gte=fourteendaysbefore, status=models.APP_INVITED)
        self.stdout.write('Checking too soon...%s found' % too_soons.count())
        msgs = []
        for app in too_soons:
            app.deadline_reminder()
            # msgs.append(emails.create_deadline_email(app))
        connection = mail.get_connection()
        connection.send_messages(msgs)
        self.stdout.write(self.style.SUCCESS(
            'Sending deadlined... Successfully sent %s too soons' % len(msgs)))

        thirteendaysago = timezone.now() - timedelta(days=13)
        self.stdout.write('Checking reminders...')
        reminders = models.Application.objects.filter(
            status_update_date__lte=thirteendaysago, status=models.APP_INVITED)
        self.stdout.write('Checking reminders...%s found' % reminders.count())
        self.stdout.write('Sending reminders...')
        msgs = []
        for app in reminders:
            app.last_reminder()
            msgs.append(emails.create_lastreminder_email(app))

        connection = mail.get_connection()
        connection.send_messages(msgs)
        self.stdout.write(self.style.SUCCESS(
            'Sending reminders... Successfully sent %s reminders' % len(msgs)))

        onedayago = timezone.now() - timedelta(days=1)
        self.stdout.write('Checking expired...')
        expired = models.Application.objects.filter(
            status_update_date__lte=onedayago, status=models.APP_LAST_REMIDER)
        if timezone.now() > HACKATHON_APP_DEADLINE:
            deadlined = models.Application.objects.filter(status=models.APP_DEADLINE_REMINDER)
            expired = expired | deadlined
        self.stdout.write('Checking expired...%s found' % expired.count())
        self.stdout.write('Setting expired...')
        count = len([app.expire() for app in expired])
        self.stdout.write(self.style.SUCCESS(
            'Setting expired... Successfully expired %s applications' % count))
