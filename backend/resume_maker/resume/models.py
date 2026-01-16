from django.db import models
from django.contrib.auth.models import User

# Create your models here.


#model to store user input
class ResumeModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_input = models.TextField()

    def __str__(self):
        return f"ResumeModel {self.id}"
    

#model to store json input
class ResumeJson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    json_input = models.JSONField()

    def __str__(self):
        return f"ResumeJson {self.id}"