from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.RegistroList.as_view(), name='registro_list'),
    path('novo/', views.RegistroCreate.as_view(), name='registro_create'),
    path('editar/<int:pk>/', views.RegistroUpdate.as_view(), name='registro_update'),
    path('excluir/<int:pk>/', views.RegistroDelete.as_view(), name='registro_delete'),

    path('usuarios/', views.UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/novo/', views.UsuarioCreate.as_view(), name='register'),
    path('usuarios/<int:pk>/status/', views.usuario_toggle_status,
         name='usuario_toggle_status'),

    path('exportar/pdf/', views.gerar_pdf_auditoria, name='gerar_pdf_auditoria'),
    path('exportar/excel/', views.exportar_selecionados,
         name='exportar_selecionados'),
    path('importar/', views.importar_planilha, name='importar_planilha'),

    path('accounts/', include('django.contrib.auth.urls')),
]
