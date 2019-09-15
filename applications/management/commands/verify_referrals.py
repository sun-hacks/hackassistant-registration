from datetime import timedelta

from django.core import mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from applications import models


class Command(BaseCommand):
    help = 'Cross checks referrals'

    def handle(self, *args, **options):
        # Get all confirmed attendees who had a referral
        applications = models.Application.objects.filter(
            status=models.APP_CONFIRMED)
        for app in applications:
            referrals = models.Application.objects.filter(
            referral = app.user.email, status=models.APP_CONFIRMED)
            app.set_referred(bool(referrals))
            for referral in referrals:
                self.stdout.write(f'{referral.user.name} was invited by {app.user.name}')
