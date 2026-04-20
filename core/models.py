from django.db import models
from django.contrib.auth.models import User


class Registro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    ativo = models.BooleanField(default=True)
    # Adicionando a data automática
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
