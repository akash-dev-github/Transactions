from django.conf.urls import url

from accounts import views

urlpatterns = [
    url(r'^$', views.AccountAPIs.as_view()),
]
