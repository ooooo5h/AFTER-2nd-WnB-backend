from django.urls import path

from users.views import KakaoOauthView, SignUpView, UserAdditionalInfoView

urlpatterns = [
    path('/kakao/oauth', KakaoOauthView.as_view()),
    path('/signup', SignUpView.as_view()),
    path('/additional-info', UserAdditionalInfoView.as_view())
]