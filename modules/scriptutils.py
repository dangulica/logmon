import os
import platform
import subprocess
import filecmp
import shutil
import concurrent.futures
from django.utils import timezone
from django.core.files import File
from django.conf import settings
from hosts.models import Host, Monitored, MonitoredHistory, Logged, LoggedHistory
from .sshutils import ssh_host
from .emailutils import email_send


def ping(ipaddress):
    pingCountParam = "-n" if platform.system().lower() == "windows" else "-c"
    with open(os.devnull, "w") as devNull:
        ret_code = subprocess.call(
            ["ping", pingCountParam, "4", "-w 5", ipaddress], stdout=devNull, stderr=devNull
        )
        print("ping done")
        result = True if ret_code == 0 else False
    return result


def monitor_host(ipaddress):
    checked_state = "UP" if ping(ipaddress) else "DOWN"
    monitored_instance = Monitored.objects.get(host__ip_address=ipaddress)
    monitored_instance.date_checked = timezone.now()
    smtp_message = "N/A"
    if monitored_instance.current_state != checked_state:
        if monitored_instance.email_notification:
            smtp_message = email_send(monitored_instance, checked_state)
        monitored_instance.current_state = checked_state
        monitored_instance.date_updated = timezone.now()
        qs_monitored_history = MonitoredHistory.objects.filter(
            monitored=monitored_instance
        ).order_by("-date")
        if len(qs_monitored_history) < monitored_instance.m_saves:
            monitored_history_new_instance = MonitoredHistory.objects.create(
                state=checked_state,
                date=timezone.now(),
                next_date=timezone.now(),
                monitored=monitored_instance
            )
            monitored_history_new_instance.save()
            qs_monitored_history[0].next_date = monitored_history_new_instance.date
            qs_monitored_history[0].save()
        else:
            qs_monitored_history[monitored_instance.m_saves - 1].date = timezone.now()
            qs_monitored_history[monitored_instance.m_saves - 1].state = checked_state
            qs_monitored_history[monitored_instance.m_saves - 1].save()
            qs_monitored_history[0].next_date = qs_monitored_history[monitored_instance.m_saves - 1].date
            qs_monitored_history[0].save()
            for i in range(monitored_instance.m_saves, len(qs_monitored_history)):
                qs_monitored_history[i].delete()
    monitored_instance.save()
    return checked_state, smtp_message


def log_host(ipaddress):
    logged_instance = Logged.objects.get(host__ip_address=ipaddress)
    logged_instance.status = ""
    if logged_instance.host.vendor.lower() == "other":
        logged_instance.status = "Model not supported"
        logged_instance.save()
    else:
        logged_instance.date_checked = timezone.now()
        if ping(ipaddress):
            tftp_path = (
                logged_instance.host.ip_address
                + "_"
                + logged_instance.date_checked.strftime("%Y%m%d%H%M%S")
                + "_config.txt"
            )
            ssh_status = ssh_host(
                ipaddress,
                logged_instance.ssh_username,
                logged_instance.ssh_password,
                logged_instance.host.vendor,
                tftp_path,
            )
            if ssh_status != "":
                logged_instance.status = ssh_status
                logged_instance.save()
                try:
                    os.remove(f"{settings.TFTP_ROOT}{tftp_path}")
                except OSError:
                    pass
            else:
                qs_logged_history = LoggedHistory.objects.filter(
                    logged=logged_instance
                ).order_by("-date")
                if qs_logged_history.exists():
                    if len(qs_logged_history) >= logged_instance.l_saves:
                        for i in range(
                            logged_instance.l_saves - 1, len(qs_logged_history)
                        ):
                            os.remove(qs_logged_history[i].filelink.path)
                            qs_logged_history[i].delete()
                    if not filecmp.cmp(
                        f"{settings.TFTP_ROOT}{tftp_path}",
                        f"{settings.PROJECT_ROOT}{qs_logged_history.first().filelink.url}",
                    ):
                        logged_instance.date_updated = logged_instance.date_checked
                        try:
                            with open(f"{settings.TFTP_ROOT}{tftp_path}") as new_file:
                                LoggedHistory(
                                    filelink=File(new_file),
                                    logged=logged_instance,
                                    date=logged_instance.date_updated,
                                ).save()
                        except OSError:
                            logged_instance.status = "ERROR: WRITE FILE"
                        if logged_instance.status != "ERROR: WRITE FILE":
                            try:
                                source_file = f"{settings.TFTP_ROOT}{tftp_path}"  # flake8 start
                                pr = settings.PROJECT_ROOT
                                mr = settings.MEDIA_URL
                                ip = logged_instance.host.ip_address
                                filename = logged_instance.date_updated.strftime("%Y%m%d%H%M%S")
                                dest_file = f'{pr}{mr}{ip}/{filename}_config.txt'
                                shutil.copyfile(source_file, dest_file)  # had to use variables for flake8 complience
                                logged_instance.status = "OK"
                            except OSError:
                                logged_instance.status = "ERROR: COPY FILE"
                    else:
                        logged_instance.status = "IDENTIC FILE"
                else:
                    logged_instance.date_updated = logged_instance.date_checked
                    try:
                        with open(f"{settings.TFTP_ROOT}{tftp_path}") as new_file:
                            LoggedHistory(
                                filelink=File(new_file),
                                logged=logged_instance,
                                date=logged_instance.date_updated,
                            ).save()
                    except OSError:
                        logged_instance.status = "ERROR: WRITE FILE"
                    if logged_instance.status != "ERROR: WRITE FILE":
                        try:
                            source_file = f"{settings.TFTP_ROOT}{tftp_path}"  # flake8 start
                            pr = settings.PROJECT_ROOT
                            mr = settings.MEDIA_URL
                            ip = logged_instance.host.ip_address
                            filename = logged_instance.date_updated.strftime("%Y%m%d%H%M%S")
                            dest_file = f'{pr}{mr}{ip}/{filename}_config.txt'
                            shutil.copyfile(source_file, dest_file)  # had to use variables for flake8 complience
                            logged_instance.status = "OK"
                        except OSError:
                            logged_instance.status = "ERROR: COPY FILE"
                try:
                    os.remove(f"{settings.TFTP_ROOT}{tftp_path}")
                except OSError:
                    logged_instance.status = "ERROR: DELETE FILE"
                logged_instance.save()
        else:
            logged_instance.status = "DOWN"
            logged_instance.save()
    if logged_instance.status == "OK" or logged_instance.status == "IDENTIC FILE":
        return True
    else:
        return False


def monitor_hosts():
    qs_hosts = Host.objects.filter(is_monitored=True).values_list(
        "ip_address", flat=True
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(monitor_host, qs_hosts)


def log_hosts():
    qs_hosts = Host.objects.filter(is_logged=True).values_list("ip_address", flat=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(log_host, qs_hosts)
