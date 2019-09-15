from datetime import timedelta

from django.core import mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from applications import models


class Command(BaseCommand):
    help = 'Cross checks referrals'

    def handle(self, *args, **options):
        # Get all confirmed attendees who had a referral
        referreds = models.Application.objects.filter(
            status=models.APP_CONFIRMED).exclude(referral="")
        for referred in referreds:
            referrers = models.Application.objects.filter(
            user__email = referred.referral)
            for referrer in referrers:
                self.stdout.write(f'{referred.user.name} was referred by {referrer.user.name}')
