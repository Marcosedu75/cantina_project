from django.db import models
from django.contrib.auth.models import User


class Usuario(models.Model):
    ROLE_CHOICES = (
        ('aluno', 'Aluno'),
        ('cantineiro', 'Cantineiro'),
    )

  
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True)
    def full_name(self):
        return self.user.get_full_name()
    
    def is_active(self):
        return self.user.is_active

    @property
    def date_joined(self):
        return self.user.date_joined
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"