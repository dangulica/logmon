from django.core.management.base import BaseCommand
from modules.scriptutils import ping
import time


class Command(BaseCommand):
    help = 'Custom Script Description'  # Put your custom help description here

    def handle(self, *args, **kwargs):
        start = time.perf_counter()
        result = ping('198.18.101.35')
        finish = time.perf_counter()
        print(f"Finished in {round(finish-start, 2)} second(s)")
        print(result)
        # Put your script here instead of pass
