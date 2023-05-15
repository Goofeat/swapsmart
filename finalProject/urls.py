from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from SwapSmart import views
from SwapSmart.views import RegisterView, LoginView, LogoutView, ConfirmView, ActivatedView, \
    InvalidTokenView, ActivateView, ProfileView, ChangePasswordView
from finalProject import settings

urlpatterns = \
    [
        path('admin/', admin.site.urls),
        path('favorites/', views.favorites, name='favorites'),
        path('accounts/', include(
            [
                path('login/', LoginView.as_view(), name='login'),
                path('register/', RegisterView.as_view(), name='signup'),
            ]
        )),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('profile/', include(
            [
                path('<str:username>/', ProfileView.as_view(), name='profile'),
                path('<str:username>/change-password/', ChangePasswordView.as_view(), name='change_password'),
            ]
        )),
        path('', include('SwapSmart.urls')),
        path('confirm/', include(
            [
                path('', ConfirmView.as_view(), name='confirm_email'),
                path('activated/', ActivatedView.as_view(), name='account_activated'),
                path('invalid-token/', InvalidTokenView.as_view(), name='invalid_token'),
            ]
        )),
        path('activate/<str:uid64>/<str:token>/', ActivateView.as_view(), name='activate'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
