from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/')
    
    voters = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='voted_project',
        blank=True
    )
    
    votes_count = models.PositiveIntegerField(default=0)

    def __str__(self):   
        return self.title

    def add_vote(self, user):
        if user.voted_project.exists():
            raise ValidationError("You have already voted for another project.")

        self.voters.add(user)
        self.votes_count = self.voters.count()
        self.save()
        return True