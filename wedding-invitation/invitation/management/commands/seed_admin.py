from django.core.management.base import BaseCommand
from invitation.mongo_db import seed_superadmin

class Command(BaseCommand):
    help = 'Seed superadmin user into MongoDB'

    def handle(self, *args, **kwargs):
        seed_superadmin()
        self.stdout.write(self.style.SUCCESS('Done.'))
