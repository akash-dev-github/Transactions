from django.conf.urls import include, url

from accounts import views

urlpatterns = [
    url(r'^$', views.ListCreateAccount.as_view(), name='accounts_list_add'),
    url(r'^(?P<pk>[0-9]+)/$', views.UpdateAccount.as_view(), name='accounts_update'),

    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),  # token based auth
]
