from rest_framework import generics,permissions
from django.contrib.auth.models import User
from .serializers import RegisterSerializer,UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)  #允许任何人访问注册接口
    serializer_class = RegisterSerializer

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)  #只有认证用户才能访问
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user  #返回当前登录的用户对象
