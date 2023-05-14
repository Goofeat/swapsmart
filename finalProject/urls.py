from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from SwapSmart.forms import LoginForm

from SwapSmart.views import IndexView, RegisterView, LoginView, LogoutView, ConfirmView, ActivatedView, \
    InvalidTokenView, ActivateView, ProfileView, ChangePasswordView
from finalProject import settings

urlpatterns = [
        path('admin/', admin.site.urls),
        path('accounts/', include(
             [
                path('login/', LoginView.as_view(), name='login'),
                path('register/', RegisterView.as_view(), name='signup'),
             ]
        )),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('profile/', include(
            [
                path('', ProfileView.as_view(), name='profile'),
                path('change-password/', ChangePasswordView.as_view(), name='change_password'),
            ]
        )),
        path('', include('SwapSmart.urls')),
        # path('applications/', include(
        #     [
        #         path('', ApplicationListView.as_view(), name='applications'),
        #         path('<int:enrollment_id>/', include(
        #             [
        #                 path('accept/', ApplicationAcceptView.as_view(), name='application_accept'),
        #                 path('decline/', ApplicationDeclineView.as_view(), name='application_decline'),
        #                 path('delete/', ApplicationDeleteView.as_view(), name='application_delete'),
        #             ]
        #         )),
        #     ]
        # )),
        path('confirm/', include(
            [
                path('', ConfirmView.as_view(), name='confirm_email'),
                path('activated/', ActivatedView.as_view(), name='account_activated'),
                path('invalid-token/', InvalidTokenView.as_view(), name='invalid_token'),
            ]
        )),
        path('activate/<str:uid64>/<str:token>/', ActivateView.as_view(), name='activate'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
