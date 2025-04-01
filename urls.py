from django.urls import path
from . import views

urlpatterns = [
    path('testedistribuicao2/', views.Teste.as_view(), name='testing'),
    path('testedistribuicao2/<int:pk>', views.Teste2.as_view(), name='testing2'),
    path('teste3/', views.Teste3.as_view(), name='teste3')
]