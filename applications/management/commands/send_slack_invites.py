from datetime import timedelta

from django.core import mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from app import slack
from app.slack import SlackInvitationException

from applications import models, emails


class Command(BaseCommand):
    help = 'Sends slack invites to all confirmed hackers'

    def handle(self, *args, **options):
        self.stdout.write('Collecting confirmed hackers...')
        hackers = models.Application.objects.filter(status=models.APP_CONFIRMED)
        self.stdout.write('Checking hackers...%s found' % hackers.count())
        self.stdout.write('Sending slack invites...')
        for app in hackers:
            try:
                slack.send_slack_invite(app.user.email)
            # Ignore if we can't send, it's only optional
            except SlackInvitationException as e:
                self.stdout.write("Failed to send invite to: %s" % app.user.email)
        self.stdout.write('Finished sending invites!')
