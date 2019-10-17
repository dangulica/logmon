from django.contrib import admin
from .models import Host, Monitored, MonitoredHistory, Logged, LoggedHistory

# Register your models here.

admin.site.register(Host)
admin.site.register(Monitored)
admin.site.register(MonitoredHistory)
admin.site.register(Logged)
admin.site.register(LoggedHistory)
