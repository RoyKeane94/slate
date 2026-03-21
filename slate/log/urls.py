from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('health/', views.health),
    path('favicon.svg', views.favicon),
    path('', views.landing),
    path('app/', RedirectView.as_view(url='/', permanent=False)),
    path('create/', views.create_household),
    path('join/', views.join_household),
    path('log/', views.log_view),
    path('log/entry/', views.save_entry),
    path('log/entries/<int:year>/<int:month>/', views.entries_for_month),
]
