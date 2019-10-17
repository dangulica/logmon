from django.core.management.base import BaseCommand
from modules.scriptutils import log_hosts
import time


class Command(BaseCommand):
    help = 'Custom Script Description'  # Put your custom help description here

    def handle(self, *args, **kwargs):
        start = time.perf_counter()
        log_hosts()
        finish = time.perf_counter()
        print(f"Finished in {round(finish-start, 2)} second(s)")
