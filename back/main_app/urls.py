from django.urls import path

import main_app.views as views

# Client
urlpatterns = [
    # path('test', views.TestView.as_view(), name='test'),
    # path('test', views.Home, name='test'),
    path('stream', views.Main, name='test2'),
    path('frame', views.FrameView.as_view(), name='test3'),
    path('statistics', views.Statistics.as_view(), name='statistics'),
]
