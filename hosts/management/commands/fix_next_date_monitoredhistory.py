from django.core.management.base import BaseCommand
from hosts.models import Host, Monitored, MonitoredHistory


class Command(BaseCommand):
    help = """The next_date field was added into MonitoredHistory model after the inital
     database migration. This scripts updates next_date field for hosts that were
     already in the database"""  # Put your custom help description here

    def handle(self, *args, **kwargs):
        print("starting")
        qs_hosts = Host.objects.all()
        for host in qs_hosts:
            print(f"processing host {host}")
            monitored_instance = Monitored.objects.get(host=host)
            qs_monhist = MonitoredHistory.objects.filter(
                monitored=monitored_instance
            ).order_by("-date")
            for index in range(len(qs_monhist)):
                print(f"processing index {index}, date {qs_monhist[index].date}")
                if index == 0:
                    qs_monhist[index].next_date = qs_monhist[index].date
                    qs_monhist[index].save()
                else:
                    qs_monhist[index].next_date = qs_monhist[index - 1].date
                    qs_monhist[index].save()
        print("finished")
