from django.urls import path
from .views import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
my_app = 'info'
urlpatterns =[
    path('', auth_views.LoginView.as_view(template_name='homepage.html'),name='home'),
    path('about_us/',About_Us.as_view(),name='about_us'),
    path('accounts/logout/', auth_views.LogoutView.as_view(),name='logout'),
    path('register/',Register.as_view(),name='register'),
    path('tnc/',TemplateView.as_view(template_name='agreement.html'),name='agree'),
    path('services/',TemplateView.as_view(template_name='services.html'),name='services'),
    path('privacy_policy/',TemplateView.as_view(template_name='privacy_policy.html'),name='privacy_policy'),
    path('license/',TemplateView.as_view(template_name='license.html'),name='license'),
    path('change_password/',auth_views.PasswordChangeView.as_view(template_name='password_change_form.html',success_url=reverse_lazy('info:password_change_done')),name='change_password'),
    path('change_password_done/',auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),name='password_change_done'),
    path('profile/',ProfileDetail.as_view(),name='profile-create'),
    path('profile_update/<int:pk>/',ProfileDetail.as_view(),name='update'),
    path('profile-list/', ProfileListView.as_view(), name='profile-list'),
    path('profile-detail/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('request/<int:pk>/', Request.as_view(), name='request'),
    path('payment/',PaymentView.as_view(),name='payment'),
    path('download/',BackUp.as_view())
]
