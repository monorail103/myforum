from django.db import models

# Create your models here.
class Thread(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    # 表示するときにタイトルを返す
    def __str__(self):
        return self.title

class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 表示するときにタイトルを返す
    def __str__(self):
        return f'{self.author}: {self.content[:30]}'