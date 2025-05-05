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
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class Teste(generics.ListCreateAPIView):
    queryset = modelDistribuicaoV2.objects.all()
    serializer_class = DistribuicaoV2Serializer

class Teste2(generics.RetrieveUpdateAPIView):
    queryset = modelDistribuicaoV2.objects.all()
    serializer_class = DistribuicaoV2Serializer

class Teste3(APIView):

    def post(self, requests):

        token = '38590d5eb1d0ec038d34057b004022eb8f2624eb'
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



class Teste4(generics.RetrieveUpdateAPIView):
    serializer_class = DistribuicaoV2Serializer
    lookup_field = 'idAgente'

    def get_queryset(self):
        idAgente = self.kwargs['idAgente']
        logger.info(f"Getting queryset for idAgente: {idAgente}")
        return modelDistribuicaoV2.objects.filter(idAgente=idAgente, id_monitoria__isnull=True)

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.first()
        if obj is None:
            logger.error(f"Object not found for idAgente: {self.kwargs['idAgente']}")
            raise status.HTTP_404_NOT_FOUND
        logger.info(f"Object found: {obj}")
        return obj

    def get(self, request, *args, **kwargs):
        logger.info(f"GET request received for idAgente: {kwargs['idAgente']}")
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"GET request successful, returning data: {serializer.data}")
            return Response(serializer.data)
        except status.HTTP_404_NOT_FOUND:
            logger.warning(f"GET request failed: Object not found for idAgente: {kwargs['idAgente']}")
            return Response({"message": "No record found with id_monitoria null"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        logger.info(f"PUT request received for idAgente: {kwargs['idAgente']}")
        logger.info(f"PUT request data: {request.data}")
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True) #add partial=True
            if serializer.is_valid():
                serializer.save()
                logger.info(f"PUT request successful, data updated: {serializer.data}")
                return Response(serializer.data)
            else:
                logger.error(f"PUT request failed: Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except status.HTTP_404_NOT_FOUND:
            logger.warning(f"PUT request failed: Object not found for idAgente: {kwargs['idAgente']}")
            return Response({"message": "No record found with id_monitoria null"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"PUT request failed: An unexpected error occurred: {e}")
            return Response({"message": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Teste5(generics.ListAPIView):
    serializer_class = DistribuicaoV2Serializer
    lookup_field = 'idAgente'

    def get_queryset(self):
        idAgente = self.kwargs['idAgente']
        logger.info(f"Getting queryset for idAgente: {idAgente}")
        return modelDistribuicaoV2.objects.filter(idAgente=idAgente, id_monitoria__isnull=False).exclude(feedback=True)

    def get(self, request, *args, **kwargs):
        logger.info(f"GET request received for idAgente: {kwargs['idAgente']}")
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                logger.warning(f"No records found for idAgente: {kwargs['idAgente']}")
                return Response({"message": "No records found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"GET request successful, returning {len(serializer.data)} records")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"GET request failed: An unexpected error occurred: {e}")
            return Response({"message": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteAllData(APIView):
    """
    API endpoint to delete all data from the modelDistribuicaoV2 table.
    """
    def delete(self, request, format=None):
        """
        Deletes all records from the modelDistribuicaoV2 table.
        """
        try:
            deleted_count, _ = modelDistribuicaoV2.objects.all().delete()
            logger.info(f"Deleted {deleted_count} records from modelDistribuicaoV2")
            return Response({"message": f"All data deleted successfully. {deleted_count} records were deleted."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting data from modelDistribuicaoV2: {e}")
            return Response({"message": "An error occurred while deleting data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
