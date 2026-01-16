from django.db import models

# Create your models here.


#model to store user input
class ResumeModel(models.Model):
    user_input = models.TextField()

    def __str__(self):
        return f"ResumeModel {self.id}"
    
    
#model to store json input
class ResumeJson(models.Model):
    json_input = models.JSONField()

    def __str__(self):
        return f"ResumeJson {self.id}"