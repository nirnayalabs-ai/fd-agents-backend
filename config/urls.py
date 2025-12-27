from django.urls import path, include

urlpatterns = [
    path('api/accounts/', include('accounts_app.urls')),
    path('api/orgs/', include('orgs_app.urls')),
    path('api/core/', include('core_app.urls')),
]
