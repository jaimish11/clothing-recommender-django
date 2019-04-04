from django.urls import path, include
from . import views

urlpatterns = [
	path('', views.index, name = 'index'),
	path('recommended/', views.RecommendedListView, name = 'recommended'),
	path('item/<int:pk>', views.ItemDetailView, name = 'item-detail'),
	path('item/like/', views.ItemLikeToggleView, name = 'like-toggle'),
	path('item/likes', views.ItemLikeAllToggleView, name = 'like-all-toggle'),
	path('items', views.ItemsAllView.as_view(), name = 'items'),
	path('items/liked/<int:pk>', views.AllLikedItemsView, name = 'allliked'),
	path('preference/filter', views.PreferenceFilterView, name = 'preference-filter'),
	path('user/statistics', views.ChartView, name = 'stats'),
]