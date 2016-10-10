from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^accounts/', include('accounts.urls')),
    url(r'^payment/', include('payments.urls')),

    url(r'^docs/', include('rest_framework_docs.urls')),

    url(r'^admin/', admin.site.urls),
]

