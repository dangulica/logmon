from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class Host(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(protocol="IPv4", unique=True)
    id_client = models.IntegerField()
    hostname = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=50, blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    vendor = models.CharField(
        max_length=50,
        choices=[
            ("Fortigate", "Fortigate"),
            ("Cisco", "Cisco"),
            ("Juniper", "Juniper"),
            ("Huawei", "Huawei"),
            ("Raisecom", "Raisecom"),
            ("Other", "Other / No backup")
        ],
    )
    is_monitored = models.BooleanField(default=True)
    is_logged = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Hosts"

    def __str__(self):
        return self.ip_address

    def get_absolute_url(self):
        return reverse("home-page")

    def first_config(self):
        logged_instance = Logged.objects.get(host=self)
        qs = LoggedHistory.objects.filter(logged=logged_instance).order_by("-date")
        if qs.exists():
            return qs[0].filelink.url
        else:
            return "#"


class Monitored(models.Model):
    host = models.OneToOneField(Host, on_delete=models.CASCADE)
    m_saves = models.PositiveSmallIntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    current_state = models.CharField(
        max_length=4, choices=[("UP", "UP"), ("DOWN", "DOWN")], default="UP"
    )
    date_updated = models.DateTimeField(default=timezone.now)
    date_checked = models.DateTimeField(default=timezone.now)
    email_notification = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Monitored"

    def __str__(self):
        return self.host.ip_address


class MonitoredHistory(models.Model):
    monitored = models.ForeignKey(Monitored, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    state = models.CharField(
        max_length=4, choices=[("UP", "UP"), ("DOWN", "DOWN")], default="UP"
    )

    class Meta:
        verbose_name_plural = "Monitored History"

    def __str__(self):
        return self.monitored.host.ip_address


class Logged(models.Model):
    host = models.OneToOneField(Host, on_delete=models.CASCADE)
    l_saves = models.PositiveSmallIntegerField(
        default=30, validators=[MinValueValidator(1), MaxValueValidator(365)]
    )
    date_updated = models.DateTimeField(default=timezone.now)
    date_checked = models.DateTimeField(default=timezone.now)
    ssh_username = models.CharField(max_length=50)
    ssh_password = models.CharField(max_length=50)
    status = models.CharField(max_length=500, default="OK")

    class Meta:
        verbose_name_plural = "Logged"

    def __str__(self):
        return self.host.ip_address


def file_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<host.ip_address>/<filename>
    return f'{instance.logged.host.ip_address}/{instance.logged.date_updated.strftime("%Y%m%d%H%M%S")}_config.txt'


class LoggedHistory(models.Model):
    logged = models.ForeignKey(Logged, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    filelink = models.FileField(upload_to=file_path)

    class Meta:
        verbose_name_plural = "Logged History"

    def __str__(self):
        return self.logged.host.ip_address
