from django.urls import path
from .views import (
    PromotionListView,
    PromotionDetailView,
    PromotionCreateView,
    PromotionUpdateView,
    PromotionDeleteView
)

app_name = 'promotions'

urlpatterns = [
    path('', PromotionListView.as_view(), name='promotion_list'),
    path('<int:pk>/', PromotionDetailView.as_view(), name='promotion_detail'),
    path('create/', PromotionCreateView.as_view(), name='promotion_create'),
    path('<int:pk>/edit/', PromotionUpdateView.as_view(), name='promotion_edit'),
    path('<int:pk>/delete/', PromotionDeleteView.as_view(), name='promotion_delete'),
]