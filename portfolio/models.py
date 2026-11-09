from django.db import models

class ContactLead(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, default='Project Inquiry')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ChatInteraction(models.Model):
    user_query = models.TextField()
    ai_response = models.TextField()
    engine = models.CharField(max_length=100, default='rag-local')
    sources = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat at {self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.user_query[:50]}..."
