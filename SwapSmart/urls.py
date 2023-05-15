from django.urls import path, include

from SwapSmart import views
from SwapSmart.views import IndexView, DeleteAdView, UpdateAdView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('search/', views.search_view, name='search'),
    path('<str:category>/', views.ad_list, name='ad_list'),
    path('<str:category>/<int:ad>/', views.ad_detail, name='ad_detail'),
    path('ad/', include(
        [
            path('new/', views.new_ad, name='new_ad'),
            path('<int:pk>/', include(
                [
                    path('delete/', DeleteAdView.as_view(), name='delete_ad'),
                    path('update/', UpdateAdView.as_view(), name='update_ad'),
                    path('unfav/', views.delete_from_favorite, name='delete_favorite'),
                    path('favorite/', views.add_to_favorite, name='add_to_favorite'),
                ]
            )),
        ]
    )),
]

# handler404 = Handler404View.as_view()
