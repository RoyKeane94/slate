from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('log.urls')),
]

handler404 = 'log.views.error_404'
handler500 = 'log.views.error_500'
handler403 = 'log.views.error_403'
