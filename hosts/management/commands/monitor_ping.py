# import sys
from django.core.management.base import BaseCommand
from modules.scriptutils import monitor_hosts
import time


class Command(BaseCommand):
    help = "Displays current time"

    def handle(self, *args, **kwargs):
        start = time.perf_counter()
        monitor_hosts()
        finish = time.perf_counter()
        print(f"Finished in {round(finish-start, 2)} second(s)")
