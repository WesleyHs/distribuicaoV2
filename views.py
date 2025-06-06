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
import numpy as np
import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Obtém a URL base do .env
URL_BASE = os.getenv('URL_BASE')
if not URL_BASE:
    raise ValueError("URL_BASE não encontrada no arquivo .env")

logger = logging.getLogger(__name__)

class Teste(generics.ListCreateAPIView):
    queryset = modelDistribuicaoV2.objects.all()
    serializer_class = DistribuicaoV2Serializer

class Teste2(generics.RetrieveUpdateAPIView):
    queryset = modelDistribuicaoV2.objects.all()
    serializer_class = DistribuicaoV2Serializer

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
    
class CompareStatus(APIView):
    """
    API endpoint to compare status between distribuicaoV2 and quadro_metas
    """
    
    def clean_dataframe_for_json(self, df):
        """Clean DataFrame to ensure JSON compliance"""
        # Replace NaN, inf, -inf with None
        df = df.replace([np.nan, np.inf, -np.inf], None)
        return df
    
    def safe_to_dict(self, row):
        """Safely convert pandas row to dict, handling NaN values"""
        result = {}
        for key, value in row.items():
            if pd.isna(value):
                result[key] = None
            elif isinstance(value, (np.integer, np.floating)):
                if np.isnan(value) or np.isinf(value):
                    result[key] = None
                else:
                    result[key] = value.item()  # Convert numpy types to Python types
            else:
                result[key] = value
        return result
    
    def get(self, request, format=None):
        try:
            token = os.getenv('TOKEN_API')
            headers = {
                'Authorization': f'Token {token}'
            }
            
            # Fetch data from first endpoint
            url8 = f"{URL_BASE}distribuicaoV3/"
            try:
                url8_response = r.get(url8, headers=headers)
                url8_response.raise_for_status()
                url8_data = url8_response.json()
                ddf = pd.DataFrame(url8_data)
            except Exception as e:
                logger.error(f"Error fetching data from testedistribuicao2: {e}")
                return Response(
                    {"message": "Error fetching distribution data"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Fetch data from quadro endpoint
            quadro_url = f"{URL_BASE}quadro_metas"
            try:
                quadro_response = r.get(quadro_url, headers=headers)
                quadro_response.raise_for_status()
                df_quadro2 = pd.DataFrame(quadro_response.json())
            except Exception as e:
                logger.error(f"Error fetching data from quadro_metas: {e}")
                return Response(
                    {"message": "Error fetching quadro data"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Validate required columns exist
            required_cols_ddf = ['nome', 'idAgente', 'status']
            required_cols_quadro = ['nome', 'status']
            
            missing_cols_ddf = [col for col in required_cols_ddf if col not in ddf.columns]
            missing_cols_quadro = [col for col in required_cols_quadro if col not in df_quadro2.columns]
            
            if missing_cols_ddf or missing_cols_quadro:
                logger.error(f"Missing columns - ddf: {missing_cols_ddf}, quadro: {missing_cols_quadro}")
                return Response(
                    {"message": "Required columns missing from data"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Filter quadro data
            df_quadro2 = df_quadro2[
                (df_quadro2['mensuracao'] != '') & 
                (df_quadro2['mensuracao'] != '-') &
                (df_quadro2['mensuracao'] != 'Sem Mensuração')
            ]

            # Clean DataFrames before merge
            ddf = self.clean_dataframe_for_json(ddf)
            df_quadro2 = self.clean_dataframe_for_json(df_quadro2)

            # Compare status between url8 and quadro
            status_comparison = pd.merge(
                ddf[['nome', 'idAgente', 'status']], 
                df_quadro2[['nome', 'status']], 
                on='nome',
                how='left',
                suffixes=('_atual', '_quadro')
            )

            # Clean the merged DataFrame
            status_comparison = self.clean_dataframe_for_json(status_comparison)

            # Find different status (handle NaN comparisons properly)
            status_comparison['status_diferente'] = (
                (status_comparison['status_atual'] != status_comparison['status_quadro']) &
                (status_comparison['status_atual'].notna()) &
                (status_comparison['status_quadro'].notna())
            )
            
            different_status = status_comparison[status_comparison['status_diferente']]

            # Build result with safe conversion
            result = []
            for _, row in different_status.iterrows():
                try:
                    item = self.safe_to_dict({
                        'nome': row['nome'],
                        'id': row['idAgente'],
                        'status_atual': row['status_atual'],
                        'status_quadro': row['status_quadro']
                    })
                    result.append(item)
                except Exception as e:
                    logger.warning(f"Error processing row: {e}, skipping...")
                    continue

            logger.info(f"Successfully compared status, found {len(result)} differences")
            return Response(result, status=status.HTTP_200_OK)

        except pd.errors.EmptyDataError:
            logger.error("One of the DataFrames is empty")
            return Response(
                {"message": "No data available for comparison"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error comparing status: {e}")
            return Response(
                {"message": "An unexpected error occurred while comparing status"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ComparativoAreaView(APIView):
    """
    API endpoint para comparar áreas/departamentos entre distribuição atual e quadro de metas
    """
    
    def clean_dataframe_for_json(self, df):
        """Clean DataFrame to ensure JSON compliance"""
        # Replace NaN, inf, -inf with None
        df = df.replace([np.nan, np.inf, -np.inf], None)
        return df
    
    def safe_to_dict(self, row):
        """Safely convert pandas row to dict, handling NaN values"""
        result = {}
        for key, value in row.items():
            if pd.isna(value):
                result[key] = None
            elif isinstance(value, (np.integer, np.floating)):
                if np.isnan(value) or np.isinf(value):
                    result[key] = None
                else:
                    result[key] = value.item()  # Convert numpy types to Python types
            else:
                result[key] = value
        return result
    
    def get(self, request, format=None):
        try:
            token = os.getenv('TOKEN_API')
            headers = {
                'Authorization': f'Token {token}'
            }
            
            # Fetch data from first endpoint
            url8 = f"{URL_BASE}distribuicaoV3/"
            try:
                url8_response = r.get(url8, headers=headers)
                url8_response.raise_for_status()
                url8_data = url8_response.json()
                ddf = pd.DataFrame(url8_data)
            except Exception as e:
                logger.error(f"Error fetching data from testedistribuicao2: {e}")
                return Response(
                    {"message": "Error fetching distribution data"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Fetch data from quadro endpoint
            quadro_url = f"{URL_BASE}quadro_metas"
            try:
                quadro_response = r.get(quadro_url, headers=headers)
                quadro_response.raise_for_status()
                df_quadro2 = pd.DataFrame(quadro_response.json())
            except Exception as e:
                logger.error(f"Error fetching data from quadro_metas: {e}")
                return Response(
                    {"message": "Error fetching quadro data"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Validate required columns exist
            required_cols_ddf = ['nome', 'idAgente', 'departamento']
            required_cols_quadro = ['nome', 'departamento']
            
            missing_cols_ddf = [col for col in required_cols_ddf if col not in ddf.columns]
            missing_cols_quadro = [col for col in required_cols_quadro if col not in df_quadro2.columns]
            
            if missing_cols_ddf or missing_cols_quadro:
                logger.error(f"Missing columns - ddf: {missing_cols_ddf}, quadro: {missing_cols_quadro}")
                return Response(
                    {"message": "Required columns missing from data"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Filter quadro data
            df_quadro2 = df_quadro2[
                (df_quadro2['mensuracao'] != '') & 
                (df_quadro2['mensuracao'] != '-') &
                (df_quadro2['mensuracao'] != 'Sem Mensuração')
            ]

            # Clean DataFrames before merge
            ddf = self.clean_dataframe_for_json(ddf)
            df_quadro2 = self.clean_dataframe_for_json(df_quadro2)

            # Compare departments between url8 and quadro
            dept_comparison = pd.merge(
                ddf[['nome', 'idAgente', 'departamento']], 
                df_quadro2[['nome', 'departamento']], 
                on='nome',
                how='left',
                suffixes=('_atual', '_quadro')
            )

            # Clean the merged DataFrame
            dept_comparison = self.clean_dataframe_for_json(dept_comparison)

            # Find different departments (handle NaN comparisons properly)
            dept_comparison['dept_diferente'] = (
                (dept_comparison['departamento_atual'] != dept_comparison['departamento_quadro']) &
                (dept_comparison['departamento_atual'].notna()) &
                (dept_comparison['departamento_quadro'].notna())
            )
            
            different_depts = dept_comparison[dept_comparison['dept_diferente']]

            # Build result with safe conversion
            result = []
            for _, row in different_depts.iterrows():
                try:
                    item = self.safe_to_dict({
                        'nome': row['nome'],
                        'id': row['idAgente'],
                        'departamento_atual': row['departamento_atual'],
                        'departamento_quadro': row['departamento_quadro']
                    })
                    result.append(item)
                except Exception as e:
                    logger.warning(f"Error processing row: {e}, skipping...")
                    continue

            logger.info(f"Successfully compared departments, found {len(result)} differences")
            return Response(result, status=status.HTTP_200_OK)

        except pd.errors.EmptyDataError:
            logger.error("One of the DataFrames is empty")
            return Response(
                {"message": "No data available for comparison"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error comparing departments: {e}")
            return Response(
                {"message": "An unexpected error occurred while comparing departments"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class Teste3(APIView):
    def post(self, request):
        try:
            # Pega o token do .env
            token = os.getenv('TOKEN_API')
            if not token:
                logger.error("TOKEN_API não encontrado no arquivo .env")
                return Response({
                    "message": "Token não configurado",
                    "error": "TOKEN_API não encontrado no arquivo .env"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            quadro = f"{URL_BASE}quadro_metas"
            atribuido = f"{URL_BASE}atribuicao"
            url8 = f"{URL_BASE}distribuicaoV3/"
            headers = {
                'Authorization': f'Token {token}'
            }

            quadro2 = r.get(quadro, headers=headers)
            atribuicao2 = r.get(atribuido, headers=headers)

            df_quadro2 = pd.DataFrame(quadro2.json())
            df_quadro2 = df_quadro2[
                (df_quadro2['mensuracao'] != '') & 
                (df_quadro2['mensuracao'] != '-') &
                (df_quadro2['mensuracao'] != 'Sem Mensuração')
            ]
            df_atribuido2 = pd.DataFrame(atribuicao2.json())
            
            df_ativo = df_quadro2[df_quadro2['status'] == 'Ativo']
            df_inativo = df_quadro2[df_quadro2['status'] != 'Ativo']

            departamentos_resultados = {}

            for departamento in df_ativo['departamento'].unique():
                df_quadro = df_ativo[df_ativo['departamento'] == departamento]
                df_atribuido = df_atribuido2[df_atribuido2['setor_quadro'] == departamento]
                
                if len(df_quadro) == 0 or len(df_atribuido) == 0:
                    print(f"Departamento sem monitor ou deparamento não é monitorado {departamento}")
                    continue
                
                monitores = df_atribuido['monitor'].tolist()
                
                if not monitores:
                    print(f"Sem monitores para o departamento: {departamento}")
                    continue
                
                df_resultado = pd.DataFrame()
                
                for _, row in df_atribuido.iterrows():
                    monitor = row['monitor']
                    pessoas = row['pessoas']
                    
                    df_monitor = df_quadro.sample(n=pessoas, replace=False) if len(df_quadro) >= pessoas else df_quadro
                    df_monitor['monitor'] = monitor
                    df_monitor['casosMonitorados'] = row['casosMonitorados']
                    
                    df_resultado = pd.concat([df_resultado, df_monitor])
                    df_quadro = df_quadro.drop(df_monitor.index)
                
                df_resultado = df_resultado[['monitor', 'nome', 'id', 'departamento', 'status', 'email', 'casosMonitorados']].copy()
                
                df_resultado = df_resultado.sort_values(by=['monitor', 'nome']).reset_index(drop=True)
                
                df_resultado['id_distribuicao'] = range(1, len(df_resultado) + 1)
                
                df_resultado['numero_monitoria'] = df_resultado.groupby(['monitor', 'nome']).cumcount() + 1
                
                df_resultado['departamento'] = departamento
                
                departamentos_resultados[departamento] = df_resultado

            # Tratando os inativos
            df_inativo['monitor'] = 'caroline'
            df_inativo['casosMonitorados'] = 1
            df_inativo['id_distribuicao'] = range(1, len(df_inativo) + 1)
            df_inativo['numero_monitoria'] = 1

            # Concatenando ativos e inativos
            df_final = pd.concat([pd.concat(departamentos_resultados.values()), df_inativo])
            df_final = df_final.reset_index(drop=True)
        
            for dept, result in departamentos_resultados.items():
                print(f"\nResultados para {dept}:")

            df_final = df_final.rename(
                columns={
                    'id': 'idAgente',
                    'id_distribuicao': 'id', 
                    'casosMonitorados': 'previsto'
                })

            # Converter colunas numéricas
            numeric_cols = df_final.select_dtypes(include=['float64']).columns
            for col in numeric_cols:
                df_final[col] = df_final[col].fillna(0).astype(int)

            # Processar cada linha
            results = []
            for index, row in df_final.iterrows():
                try:
                    data = row.to_dict()
                    # Remover valores NaN
                    data = {k: v for k, v in data.items() if pd.notna(v)}
                    # Fazer o POST
                    response = r.post(url8, json=data, headers=headers)
                    response.raise_for_status()
                    results.append(data)
                except Exception as e:
                    logger.error(f"Error posting row {index}: {str(e)}")
                    continue

            if not results:
                return Response({"message": "No data was successfully processed"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": "Data processed successfully",
                "total_records": len(results),
                "data": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in Teste3: {str(e)}")
            return Response({
                "message": "An error occurred while processing the data",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class UpdateMonitoria(generics.RetrieveUpdateAPIView):
    serializer_class = DistribuicaoV2Serializer
    lookup_field = 'id_monitoria'
    lookup_url_kwarg = 'id_monitoria'

    def get_queryset(self):
        id_monitoria = self.kwargs['id_monitoria']
        logger.info(f"Getting queryset for id_monitoria: {id_monitoria}")
        return modelDistribuicaoV2.objects.filter(id_monitoria=id_monitoria)

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.first()
        if obj is None:
            logger.error(f"Object not found for id_monitoria: {self.kwargs['id_monitoria']}")
            raise status.HTTP_404_NOT_FOUND
        logger.info(f"Object found: {obj}")
        return obj

    def get(self, request, *args, **kwargs):
        logger.info(f"GET request received for id_monitoria: {kwargs['id_monitoria']}")
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"GET request successful, returning data: {serializer.data}")
            return Response(serializer.data)
        except status.HTTP_404_NOT_FOUND:
            logger.warning(f"GET request failed: Object not found for id_monitoria: {kwargs['id_monitoria']}")
            return Response({"message": "No record found with this id_monitoria"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        logger.info(f"PUT request received for id_monitoria: {kwargs['id_monitoria']}")
        logger.info(f"PUT request data: {request.data}")
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"PUT request successful, data updated: {serializer.data}")
                return Response(serializer.data)
            else:
                logger.error(f"PUT request failed: Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except status.HTTP_404_NOT_FOUND:
            logger.warning(f"PUT request failed: Object not found for id_monitoria: {kwargs['id_monitoria']}")
            return Response({"message": "No record found with this id_monitoria"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"PUT request failed: An unexpected error occurred: {e}")
            return Response({"message": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
