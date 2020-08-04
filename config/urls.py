from django.contrib import admin
from django.urls import path, include
from rest_auth.urls import LoginView, LogoutView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Quizzes API",
      default_version='v1',
      description="Description",
      contact=openapi.Contact(email="bobrov.v1ad3@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/login/', LoginView.as_view()),
    path('api/v1/auth/logout/', LogoutView.as_view()),

    path('api/v1/', include('quiz.urls')),

    path('openapi/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
