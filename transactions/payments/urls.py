from django.conf.urls import url

from payments import views

urlpatterns = [
    url(r'^$', views.PaymentApis.as_view(), name="payment_add_list"),
]
