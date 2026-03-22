from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from . import views

# API routes used by the iOS app (no cookies / CSRF token). Exempt at URL level so
# the wrapper is definitely outermost — @csrf_exempt above @require_POST on the view
# can still be blocked by CSRF middleware in some Django versions.
urlpatterns = [
    path('health/', views.health),
    path('favicon.svg', views.favicon),
    path('', views.landing),
    path('app/', RedirectView.as_view(url='/', permanent=False)),
    path('create/', csrf_exempt(views.create_household)),
    path('join/', csrf_exempt(views.join_household)),
    path('log/', views.log_view),
    path('log/entry/', csrf_exempt(views.save_entry)),
    path('log/entries/<int:year>/<int:month>/', csrf_exempt(views.entries_for_month)),
]
