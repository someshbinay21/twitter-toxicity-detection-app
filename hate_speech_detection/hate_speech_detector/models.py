from django.db import models


class TwitterUser(models.Model):
    screen_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.screen_name


class Tweet(models.Model):
    user = models.ForeignKey(TwitterUser, on_delete=models.CASCADE)
    text = models.TextField()
    is_toxic = models.BooleanField(default=False)
    toxicity_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.screen_name}: {self.text}"
