from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    DocumentViewSet, AuthorViewSet, PaperImageViewSet, ReferenceViewSet,
    SectionViewSet, process_ai_command, export_latex, get_latex_source,
    export_pdf, health_check,
)
from .auth_views import RegisterView, me

router = routers.DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'images', PaperImageViewSet)
router.register(r'references', ReferenceViewSet)
router.register(r'sections', SectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health_check'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='auth_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('auth/me/', me, name='auth_me'),
    path('ai/command', process_ai_command, name='process_ai_command'),
    path('document/<int:doc_id>/latex', get_latex_source, name='get_latex_source'),
    path('document/<int:doc_id>/export/pdf', export_pdf, name='export_pdf'),
    path('document/<int:doc_id>/export/latex', export_latex, name='export_latex'),
]
