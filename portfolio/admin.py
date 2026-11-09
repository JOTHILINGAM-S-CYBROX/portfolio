from django.contrib import admin
from .models import ContactLead, ChatInteraction

@admin.register(ContactLead)
class ContactLeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)

@admin.register(ChatInteraction)
class ChatInteractionAdmin(admin.ModelAdmin):
    list_display = ('user_query', 'engine', 'created_at')
    search_fields = ('user_query', 'ai_response')
    readonly_fields = ('created_at',)
