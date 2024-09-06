from django.views.generic import ListView
from django.db.models import QuerySet

from .models import Hub


class HubsIndexView(ListView):
    paginate_by = 10
    model = Hub
    template_name = "hubs_index.html"

    def get_queryset(self) -> QuerySet[Hub]:
        return self.model.objects.order_by("title")