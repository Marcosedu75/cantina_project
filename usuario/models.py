from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    ROLE_CHOICES = (
        ('aluno', 'Aluno'),
        ('cantineiro', 'Cantineiro'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Usuario(models.Model):
    turma = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.turma})" if self.turma else self.username



