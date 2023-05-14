from django.urls import path, include

from SwapSmart import views
from SwapSmart.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('<str:category>/', views.ad_list, name='ad_list'),
    path('<str:category>/<int:ad>/', views.ad_detail, name='ad_detail'),
    path('ad/', include(
        [
            path('new/', views.new_ad, name='new_ad'),
            path('<int:pk>/', include(
                [
                    path('delete/', views.delete_ad, name='delete_ad'),
                    path('update/', views.update_ad, name='update_ad'),
                    path('send/', views.send_ad, name='enroll_ad'),
                ]
            )),
        ]
    )),
]

# handler404 = Handler404View.as_view()
