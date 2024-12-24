from django.urls import path
from .views import RouteView

urlpatterns = [
    path('', RouteView.as_view(), name='route'),
]