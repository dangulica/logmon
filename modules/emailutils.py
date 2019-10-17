import smtplib
import arrow
from django.core.mail import send_mail
from textwrap import dedent
from django.utils import timezone
from django.conf import settings


def email_message_monitored_host(h_id, ip, host, desc, ldate, last, actual):
    time_now = arrow.get(timezone.now()).to('Europe/Bucharest').strftime("%d.%b.%Y %H:%M:%S")
    time_last = arrow.get(ldate).to('Europe/Bucharest').strftime("%d.%b.%Y %H:%M:%S")
    message = dedent(
        f"""\
        Status change for host {ip} ({host} - {desc})
        \n
        On {time_now} status changed from {last} to {actual}.
        \n\n
        Last status change was on {time_last}.
        \n\n
        You can view the history here:  http://{settings.URL}/hosts/{h_id}/monitored_history/
        \n\n
        Please do not reply to this email.
        \n
        -------
        \n
        LogMon Team
        """
    )
    return message


def email_send(instance, checked_state):
    h_id = instance.host.id
    ip = instance.host.ip_address
    host = instance.host.hostname
    desc = instance.host.description
    ldate = instance.date_updated
    last = instance.current_state
    actual = checked_state
    email_subject = f"LogMon notification: Host {ip} ({host}) is {actual}"
    email_message = email_message_monitored_host(h_id, ip, host, desc, ldate, last, actual)
    email_from = settings.DEFAULT_FROM_EMAIL
    email_list = [instance.host.owner.email]
    try:
        send_mail(
            email_subject, email_message, email_from, email_list, fail_silently=False
        )
        smtp_message = "OK"
    except smtplib.SMTPException:
        smtp_message = "ERROR: SMTP"
    return smtp_message
