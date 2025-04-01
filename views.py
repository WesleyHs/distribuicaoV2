from django.shortcuts import render
from rest_framework import status, generics, response
from rest_framework.views import APIView
from .models import modelDistribuicaoV2
from .serializers import DistribuicaoV2Serializer
import requests as r
import pandas as pd
from datetime import datetime
import time
from rest_framework.response import Response


class Teste(generics.ListCreateAPIView):
    queryset = modelDistribuicaoV2.objects.all()
    serializer_class = DistribuicaoV2Serializer

class Teste2(generics.RetrieveUpdateAPIView):
    queryset = modelDistribuicaoV2.objects.all()
    serializer_class = DistribuicaoV2Serializer

class Teste3(APIView):

    def post(self, requests):

        token = ''
        quadro = 'http://127.0.0.1:8000/api/v1/quadro_metas'
        atribuido = 'http://127.0.0.1:8000/api/v1/atribuicao'
        url8 = "http://127.0.0.1:8000/api/v1/testedistribuicao2/"
        headers = {
            'Authorization': f'Token {token}'
        }
        quadro2 = r.get(quadro, headers=headers)
        atribuicao2 = r.get(atribuido, headers=headers)

        df_quadro2 = pd.DataFrame(quadro2.json())
        df_atribuido2 = pd.DataFrame(atribuicao2.json())

        departamentos_resultados = {}

        for departamento in df_quadro2['departamento'].unique():
            df_quadro = df_quadro2[df_quadro2['departamento'] == departamento]
            df_atribuido = df_atribuido2[df_atribuido2['setor'] == departamento]
            
            if len(df_quadro) == 0 or len(df_atribuido) == 0:
                print(f"Departamento sem monitor ou deparamento não é monitorado {departamento}")
                continue
            
            monitores = df_atribuido['monitor'].tolist()
            
            if not monitores:
                print(f"Sem monitores para o departamento: {departamento}")
                continue
            
            num_bins = len(monitores)
            
            if len(df_quadro) < num_bins:
                df_quadro['monitor'] = monitores[:len(df_quadro)]
            else:
                df_quadro['monitor'] = pd.qcut(range(len(df_quadro)), q=num_bins, labels=False)
                df_quadro['monitor'] = df_quadro['monitor'].apply(lambda x: monitores[int(x)])
            
            df_resultado = df_quadro[['monitor', 'nome', 'id', 'departamento', 'status','email' ]].copy()
            
            casos_monitorados = df_atribuido.set_index('monitor')['casosMonitorados']
            df_resultado['casosMonitorados'] = df_resultado['monitor'].map(casos_monitorados)
            
            df_resultado['casosMonitorados'] = df_resultado['casosMonitorados'].fillna(1).astype(int)
            
            df_resultado = df_resultado.loc[df_resultado.index.repeat(df_resultado['casosMonitorados'])]
            
            df_resultado = df_resultado.sort_values(by=['monitor', 'nome']).reset_index(drop=True)
            
            df_resultado['id_distribuicao'] = range(1, len(df_resultado) + 1)
            
            df_resultado['numero_monitoria'] = df_resultado.groupby(['monitor', 'nome']).cumcount() + 1
            
            df_resultado['departamento'] = departamento
            
            departamentos_resultados[departamento] = df_resultado

        # Combine results if needed
        df_final = pd.concat(departamentos_resultados.values())

        # Show results for each department
        for dept, result in departamentos_resultados.items():
            print(f"\nResultados para {dept}:")
        
        df_final = df_final.rename(
            columns={
                'id': 'idAgente',
                'id_distribuicao': 'id',
            })
        
        for index, row in df_final.iterrows():
            response = r.post(url8, json=row.to_dict())
            # time.sleep(4)
        fim = datetime.now()

        print("fim", fim)

        return Response(df_final.to_dict(orient='records')) 
        



