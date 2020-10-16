from django.db import models

# Create your models here.
class document(models.Model):
    file = models.FileField(upload_to= "")