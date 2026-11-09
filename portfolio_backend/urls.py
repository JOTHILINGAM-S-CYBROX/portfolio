import os
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from portfolio.views import portfolio_home, chat_api, contact_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', portfolio_home, name='home'),
    
    # RAG Chatbot endpoints
    path('api/chat/', chat_api, name='chat_api'),
    path('api/chat', chat_api, name='chat_api_noslash'),
    
    # Contact Form endpoints (compatible with existing frontend fetch)
    path('api/contact/', contact_api, name='contact_api'),
    path('api/contact', contact_api, name='contact_api_noslash'),
    
    # Direct asset serving for assets/Jothi.png, assets/sj.png
    re_path(r'^assets/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, 'assets'),
    }),
]
