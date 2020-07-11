from django.urls import path

from core.views import ChannelView, CreateChannelView

urlpatterns = [
    path('<user>/channel/', ChannelView.as_view(), name='channel'),
    path('create-channel/', CreateChannelView.as_view(), name='create_channel')
]