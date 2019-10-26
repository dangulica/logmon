from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView
from django.db.models import Q
from modules.scriptutils import monitor_host, log_host
from .models import Host, Monitored, MonitoredHistory, Logged, LoggedHistory
from .forms import HostForm, MonitoredForm, LoggedForm

# Create your views here.


class HostsListView(ListView):
    model = Host
    # template_name = 'hosts/hosts_view.html'  # <app>/<model>_<viewtype>.html
    ordering = ["-date_created"]
    paginate_by = 20


class OwnHostsListView(HostsListView):
    def get_queryset(self):
        return Host.objects.filter(owner=self.request.user).order_by("-date_created")


class HostDetailView(DetailView):
    model = Host


class SearchResultsView(ListView):
    model = Host
    template_name = "hosts/search_results.html"
    ordering = ["-date_created"]
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Host.objects.filter(
            Q(ip_address__icontains=query)
            | Q(id_client__icontains=query)
            | Q(description__icontains=query)
            | Q(hostname__icontains=query)
            | Q(vendor__icontains=query)
        ).order_by("-date_created")
        return object_list


class MonitoredHistoryListView(ListView):
    model = MonitoredHistory
    ordering = ["-date"]
    paginate_by = 20

    def get_queryset(self):
        obj = get_object_or_404(Monitored, host=self.kwargs.get("pk"))
        return MonitoredHistory.objects.filter(monitored=obj).order_by("-date")


class LoggedHistoryListView(ListView):
    model = LoggedHistory
    ordering = ["-date"]
    paginate_by = 20

    def get_queryset(self):
        obj = get_object_or_404(Logged, host=self.kwargs.get("pk"))
        return LoggedHistory.objects.filter(logged=obj).order_by("-date")


@login_required
def host_create_view(request):
    if request.method == "POST":
        h_form = HostForm(request.POST)
        m_form = MonitoredForm(request.POST)
        l_form = LoggedForm(request.POST)
        if h_form.is_valid() and m_form.is_valid() and l_form.is_valid():
            h_form.instance.owner = request.user
            h_form.save()
            m_form.instance.host = h_form.instance
            m_form.save()
            monitored_history = MonitoredHistory.objects.create(
                state=m_form.instance.current_state,
                date=timezone.now(),
                next_date=timezone.now(),
                monitored=m_form.instance,
            )
            monitored_history.save()
            l_form.instance.host = h_form.instance
            l_form.save()
            messages.info(
                request, f"Host {h_form.instance.ip_address} added", extra_tags="info"
            )
            return redirect("home-page")
    else:
        h_form = HostForm()
        m_form = MonitoredForm()
        l_form = LoggedForm()
    context = {"h_form": h_form, "m_form": m_form, "l_form": l_form}
    return render(request, "hosts/host_new.html", context)


@login_required
def host_edit_view(request, pk):
    host = Host.objects.get(id=pk)
    if request.user == host.owner:
        monitored = Monitored.objects.get(host=host)
        logged = Logged.objects.get(host=host)
        if request.method == "POST":
            h_form = HostForm(request.POST or None, instance=host)
            m_form = MonitoredForm(request.POST or None, instance=monitored)
            l_form = LoggedForm(request.POST or None, instance=logged)
            if h_form.is_valid() and m_form.is_valid() and l_form.is_valid():
                host = h_form.instance
                host.save()
                monitored = m_form.instance
                monitored.save()
                logged = l_form.instance
                logged.save()
                messages.info(
                    request, f"Host {host.ip_address} updated", extra_tags="info"
                )
                return redirect("host-detail", pk=pk)
        else:
            h_form = HostForm(instance=host)
            m_form = MonitoredForm(instance=monitored)
            l_form = LoggedForm(instance=logged)
        context = {"h_form": h_form, "m_form": m_form, "l_form": l_form, "host": host}
        return render(request, "hosts/host_edit.html", context)
    else:
        return redirect("denied")


class HostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Host
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        host = self.get_object()
        messages.success(
            self.request, f"Host {host.ip_address} deleted", extra_tags="success"
        )
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        host = self.get_object()
        if self.request.user == host.owner:
            return True
        return False


@login_required
def check(request, ipaddress):
    checked_state, smtp_message = monitor_host(ipaddress)
    if checked_state == "UP":
        messages.info(request, f"Host {ipaddress} is UP", extra_tags="success")
    else:
        messages.error(request, f"Host {ipaddress} is DOWN", extra_tags="danger")
    if smtp_message == "OK":
        messages.info(
            request, "Info email has been successfully sent", extra_tags="success"
        )
    elif smtp_message != "N/A":
        messages.error(
            request,
            f"Info email has not been sent, {smtp_message}",
            extra_tags="danger",
        )
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def backup(request, ipaddress):
    backup_state = log_host(ipaddress)
    message_status = Logged.objects.get(host__ip_address=ipaddress).status
    if backup_state:
        if message_status == "OK":
            messages.info(
                request,
                f"Backup for host {ipaddress} was saved successfully",
                extra_tags="success",
            )
        else:
            messages.info(
                request,
                f"Backup for host {ipaddress} resulted in an identic file",
                extra_tags="success",
            )
    else:
        messages.error(
            request,
            f"Backup for host {ipaddress} failed, cause: {message_status}",
            extra_tags="danger",
        )
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
