from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

app_name = 'extraction'

urlpatterns = [
    # Landing and Authentication URLs
    path('', views.LandingPageView.as_view(), name='landing'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='extraction:landing'), name='logout'),
    
    # URLs para ExtractionRequest
    path('requests/', views.ExtractionRequestListView.as_view(), name='request_list'),
    path('create/', views.ExtractionRequestCreateView.as_view(), name='request_create'),
    path('<int:pk>/', views.ExtractionRequestDetailView.as_view(), name='request_detail'),
    path('<int:pk>/send-to-analysis/', views.send_to_analysis, name='send_to_analysis'),
    
    # URLs para Procedures
    path('<int:pk>/procedures/add/', views.add_procedure, name='add_procedure'),
    path('<int:pk>/procedures/<int:procedure_id>/edit/', views.edit_procedure, name='edit_procedure'),
    path('<int:pk>/procedures/<int:procedure_id>/delete/', views.delete_procedure, name='delete_procedure'),
    
    # URLs para Documents
    path('<int:pk>/review/', views.review_request, name='review_request'),
    path('<int:pk>/documents/add/', views.add_document, name='add_document'),
    path('<int:pk>/documents/<int:document_id>/edit/', views.edit_document, name='edit_document'),
    path('<int:pk>/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('<int:pk>/view/', views.view_request, name='view_request'),
]

# Adicionar URLs para servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)