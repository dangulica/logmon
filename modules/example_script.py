from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Custom Script Description'  # Put your custom help description here

    def handle(self, *args, **kwargs):
        pass
        # Put your script here instead of pass
