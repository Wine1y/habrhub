from django.urls import path

from .views import HubsIndexView


app_name = "parsing"
urlpatterns = [
    path('', HubsIndexView.as_view(), name='hubs_index'),
]