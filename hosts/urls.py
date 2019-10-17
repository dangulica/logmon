"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views
from .views import (
    HostsListView,
    MonitoredHistoryListView,
    LoggedHistoryListView,
    SearchResultsView,
    OwnHostsListView,
    HostDetailView,
    HostDeleteView
)

urlpatterns = [
    path("", HostsListView.as_view(), name="hosts-list"),
    path("search/", SearchResultsView.as_view(), name="search_results"),
    path("own/", OwnHostsListView.as_view(), name="hosts-own"),
    path("<int:pk>/detail/", HostDetailView.as_view(), name="host-detail"),
    path("<int:pk>/edit/", views.host_edit_view, name="host-edit"),
    path('<int:pk>/delete', HostDeleteView.as_view(), name='host-delete'),
    path("check/<ipaddress>/", views.check, name="host-check"),
    path("backup/<ipaddress>/", views.backup, name="host-backup"),
    path("new/", views.host_create_view, name="host-new"),
    path(
        "<int:pk>/monitored_history/",
        MonitoredHistoryListView.as_view(),
        name="host-monitored-history",
    ),
    path(
        "<int:pk>/logged_history/",
        LoggedHistoryListView.as_view(),
        name="host-logged-history",
    ),
]
