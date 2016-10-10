from django.conf.urls import url, include

from accounts import views

urlpatterns = [
    url(r'^$', views.AccountAPIs.as_view()),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),  # token based auth
]
