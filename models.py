from django.db import models
from datetime import *

# Create your models here.
class modelDistribuicaoV2(models.Model):
    id = models.AutoField(primary_key=True) # id criado automatimente
    id_monitoria = models.CharField(max_length=250, blank=True, null=True) #irá vir do front na monitoria
    casosMonitorados = models.IntegerField(null=True, blank=True) # criado automativamente
    numero_monitoria = models.IntegerField(null=True, blank=True) # automaticamente qtde de monitoria listado 1-4 exemplo
    analise= models.CharField(max_length=250, blank=True, null=True) # entender se é qual monitoria do agente no mes
    data_monitoria = models.DateTimeField(blank=True, null=True) #data que a monitoria está sendo realizada
    status_monitoria = models.BooleanField(default=False)
    # identificadora = models.CharField(editable=False, null=True, blank=True, unique=True, max_length=250)

    # monitoriasRealizadas= models.CharField(max_length=250, blank=True, null=True) # verificar se é redundante com o casos monitorados
    previsto= models.CharField(max_length=250, blank=True, null=True) ## verificar se é redundante com o casos monitorados
    consultorias= models.CharField(max_length=250, blank=True, null=True) # entender o campo consultoria 
    intervencoes= models.CharField(max_length=250, blank=True, null=True) # entender o campo intervenções

    dataContato= models.DateTimeField(max_length=250, blank=True, null=True) # vem do front
    motivoContato= models.CharField(max_length=250, blank=True, null=True) # vem do front
    idLigacao= models.CharField(max_length=250, blank=True, null=True) # vem do front
    ticket= models.CharField(max_length=250, blank=True, null=True) # vem do front
    pedido= models.CharField(max_length=250, blank=True, null=True) # vem do front
    # F= models.CharField(max_length=250, blank=True, null=True) # vem do front
    cards= models.JSONField(blank=True, null=True) # entender esse formulario, se irá ser um json e se precisa salvar só o nome e ter outro campo com o json dos cards
    resumoCaso= models.TextField(blank=True, null=True) # vem do front
    pontoAtencao= models.TextField(blank=True, null=True) #vem do front
    elogioCliente= models.TextField(blank=True, null=True) # vem d0o0 front
    horario= models.CharField(max_length=250, blank=True, null=True) # vem do front

    inicio = models.DateTimeField(blank=True, null=True) #inicio da monitoria definir
    fim = models.DateTimeField(blank=True, null=True) #quando clica no finaliza
    # tempo_monitoria = models.DurationField(blank=True, null=True) #automatico
    tempo_monitoria = models.CharField(max_length=8, blank=True, null=True)
    nota = models.IntegerField(null=True) # nota da monitoria //verifica se ira fazer no front ou no back

    consultoria = models.BooleanField(default=False) #vem do front
    motivo_consultoria  = models.TextField(blank=True, null=True) #vem do front
    
    analista = models.CharField(blank=True, null=True, max_length=250) #nome do analista de consultoria
    consultoria_contestacao = models.BooleanField(default=False) #se a consultoria foi contestada
    motivo_contestacao_consultoria = models.CharField(blank=True, null=True, max_length=250) # qual motivo da contestacao 
    realizado_consultoria = models.BooleanField(default=False) #se a consultoria foi realizada

    data_consultoria = models.DateTimeField(blank=True, null=True) #data que a consultoria foi realizada


    intervencao = models.BooleanField(default=False) # vem do front
    motivo_intervencao = models.TextField(null=True, blank=True) 
    data_ocorrencia_intervencao = models.DateTimeField(blank=True, null=True)
    acao_intervencao = models.CharField(null=True, blank=True, max_length=250)
    observacao_intervencao = models.CharField(null=True, blank=True, max_length=250)
    data_feedback_intervencao = models.DateTimeField(blank=True, null=True)
    contestacao_intervencao = models.CharField(max_length=250, blank=True, null=True)
    motivo_contestacao_intervencao = models.CharField(max_length=250, null=True, blank=True)
    intervencao_justificativa = models.CharField(max_length=250, null=True, blank=True)
    
    idsIntervencao = models.CharField(max_length=250, null=True, blank=True)
    protocolosIntervencao = models.CharField(max_length=250, null=True, blank=True)
    data_intervencao_realizado = models.DateTimeField(blank=True, null=True)


    comentario_intervencao = models.TextField(null=True, blank=True) #front monitoria
    intervencao_feedback = models.BooleanField(default=False) #quando foi realizado o feedback
    
    alerta = models.BooleanField(default=False) #ter um botao no front
    alerta_comentario = models.TextField(blank=True, null=True)
    alerta_feedback = models.BooleanField(default=False) #quando foi realizado o alerta do feedback
    alerta_contestacao = models.TextField(blank=True, null=True)
    alerta_justificativa = models.TextField(blank=True, null=True)
    data_alerta_realizado = models.DateTimeField(blank=True, null=True)



    observacoes_feedback = models.CharField(max_length=250, blank=True, null=True) #obserrvação no feedback
    feedback = models.BooleanField(default=False) #feedback realizado ou nao realizado
    #justificativa

    contestacao = models.BooleanField(default=False) #se teve contestacao
    contestacao_motivo = models.CharField(max_length=250, blank=True, null=True) #motivo da contestacao


    aprovacao_contestacao = models.BooleanField(default=False) #se a contestação foi aprovada
    resposta_contestacao = models.TextField(blank=True, null=True) #vem do front
    causador_contestacao = models.CharField(max_length=250, blank=True, null=True) #quem causou a contestacao
    realizado_contestacao = models.BooleanField(default=False)

    retorno_contestacao = models.BooleanField(default=False)
    alterado = models.BooleanField(blank=True, null=True) #vem do front



    monitor = models.CharField(max_length=250, blank=True, null=True) #vem da monitores
    email_monitor = models.CharField(max_length=250, blank=True, null=True) #precisa do email
    id_monitor = models.IntegerField(blank=True, null=True)

    idAgente= models.CharField(max_length=250, blank=True, null=True) # vem do quadro
    nome = models.CharField(max_length=250, blank=True, null=True) #vem do quadro nome do agente
    departamento = models.CharField(max_length=250, blank=True, null=True) #vem do quadro
    status = models.CharField(max_length=250, null=True, blank=True) # vem do quadro
    email = models.CharField(max_length=250, blank=True, null=True) # vem do quadro 
    dataAdmissao= models.DateTimeField( blank=True, null=True) # vem do quadro

    supervisor = models.CharField(max_length=250, blank=True, null=True) #vem do front
    coordenador = models.CharField(max_length=250, blank=True, null=True) # vem do front
    gerente = models.CharField(max_length=250, blank=True, null=True) #vem do front
    tratado = models.BooleanField(default=False)
    
    macro_aplicada = models.CharField(max_length=250, blank=True, null=True)
    macro_correta = models.CharField(max_length=250, blank=True, null=True)
    formularioArea = models.CharField(max_length=250, blank=True, null=True)
    
    
    # funcoes novas back
    updated_at = models.DateField(auto_now=True)
    alterado_por = models.CharField(null=True, blank=True, max_length=250)
    excluido_por = models.CharField(blank=True, null=True, max_length=250)




    # def save(self, *args, **kwargs):
    #     if self.inicio and self.fim:
    #         self.tempo = self.fim - self.inicio  
    #     else:
    #         self.tempo = None 

    #     super().save(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        print(request.data)  
        return super().post(request, *args, **kwargs)
    
    # def save(self, *args, **kwargs):
    #     self.identificadora = f"{self.numero_monitoria} {self.idAgente}"
    #     super().save(*args, **kwargs)


    class Meta:
        db_table = 'distribuicaoV2'
# Create your models here.
