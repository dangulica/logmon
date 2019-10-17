from django import forms
from .models import Host, Monitored, Logged


class HostForm(forms.ModelForm):
    ip_address = forms.GenericIPAddressField(label="IP Address")
    id_client = forms.IntegerField(label="ID Client")
    is_monitored = forms.BooleanField(label="ICMP Monitored", required=False)
    is_logged = forms.BooleanField(label="Backup Config by SSH", required=False)

    class Meta:
        model = Host
        fields = [
            "ip_address",
            "id_client",
            "hostname",
            "description",
            "vendor",
            "is_monitored",
            "is_logged",
        ]


class MonitoredForm(forms.ModelForm):
    m_saves = forms.IntegerField(label="Number of status changes to keep", initial=30)
    email_notification = forms.BooleanField(label="Notify by email", required=False)

    class Meta:
        model = Monitored
        fields = ["m_saves", "email_notification"]


class LoggedForm(forms.ModelForm):
    ssh_password = forms.CharField(
        label="SSH Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Do not use AD password"}, render_value=True),
        required=False,
    )
    l_saves = forms.IntegerField(label="Number of config files to keep", initial=60)
    ssh_username = forms.CharField(label="SSH Username", required=False)

    class Meta:
        model = Logged
        fields = ["l_saves", "ssh_username", "ssh_password"]
