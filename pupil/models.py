from django.db import models


class Pupil(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE)
    learning_center = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    @property
    def is_full_personal_data(self):
        is_person = True
        return is_person

    def __str__(self):
        return self.user.username
