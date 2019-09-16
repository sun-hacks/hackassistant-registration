from datetime import timedelta

from django.core import mail
from django.core.management.base import BaseCommand
from django.utils import timezone


from applications import models, emails


class Command(BaseCommand):
    help = 'Sends get ready if it hasn\'t been sent yet'

    def handle(self, *args, **options):
        get_readys = models.Application.objects.filter(status=models.APP_CONFIRMED, sent_info=False)
        self.stdout.write('Checking confirmed...%s found' % get_readys.count())
        self.stdout.write('Sending get ready...')
        msgs = []
        for app in get_readys:
            app.send_info()
            msgs.append(emails.create_get_ready_email(app))

        connection = mail.get_connection()
        connection.send_messages(msgs)
        self.stdout.write(self.style.SUCCESS(
            'Sending reminders... Successfully sent %s reminders' % len(msgs)))
