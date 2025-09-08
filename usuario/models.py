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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    foto = models.ImageField(
        upload_to='user_fotos/',
        null=True,
        blank=True,
        default='user_fotos/default.jpg'
    )
    default='user_fotos/default.jpg'

    # Retorna o nome completo do usuário
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    def is_active(self):
        return self.user.is_active

    # Retorna a data que o usuário se cadastrou
    @property
    def date_joined(self):
        return self.user.date_joined