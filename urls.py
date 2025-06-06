from django.urls import path
from . import views

urlpatterns = [
    path('testedistribuicao2/', views.Teste.as_view(), name='testing'),
    path('testedistribuicao2/<int:pk>', views.Teste2.as_view(), name='testing2'),
    path('teste3/', views.Teste3.as_view(), name='teste3'), 
    # path('teste4/<int:idAgente>', views.Teste4.as_view(), name='teste4')
    path('teste4/<str:idAgente>/', views.Teste4.as_view(), name='teste4'),
    path('delete_all_data/', views.DeleteAllData.as_view(), name='delete_all_data'),
    path('teste5/<str:idAgente>/', views.Teste5.as_view(), name='teste5'),
    path('compare_status/', views.CompareStatus.as_view(), name='compare_status'),
    path('compare_departments/', views.ComparativoAreaView.as_view(), name='compare_departments'),
    path('update_monitoria/<str:id_monitoria>/', views.UpdateMonitoria.as_view(), name='update_monitoria'),
]