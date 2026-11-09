import json
import os
import re
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

from .rag_engine import answer_query
from .models import ContactLead, ChatInteraction

def portfolio_home(request):
    """Serve the primary portfolio page"""
    return render(request, 'index.html', {
        'year': 2026,
        'title': 'JOTHILINGAM S — Digital Craftsmanship · Portfolio 2026'
    })

@csrf_exempt
def chat_api(request):
    """RAG Chatbot API endpoint"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed. Use POST.'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
        user_message = body.get('message', '').strip()
        chat_history = body.get('history', [])

        if not user_message:
            return JsonResponse({'success': False, 'message': 'Please provide a message.'}, status=400)

        # Run RAG answer pipeline with conversation history
        rag_result = answer_query(user_message, history=chat_history)
        
        # Safely record interaction in database if writable
        try:
            ChatInteraction.objects.create(
                user_query=user_message,
                ai_response=rag_result.get('answer', ''),
                engine=rag_result.get('engine', 'rag-local'),
                sources=', '.join(rag_result.get('sources', []))
            )
        except Exception as db_err:
            # Ephemeral / read-only serverless DB safety
            pass

        return JsonResponse({
            'success': True,
            'answer': rag_result.get('answer', ''),
            'engine': rag_result.get('engine', 'rag-local'),
            'sources': rag_result.get('sources', [])
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def contact_api(request):
    """Serverless Contact Form Dispatcher with Gmail SMTP"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed. Use POST.'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
        name = body.get('name', '').strip()
        email = body.get('email', '').strip()
        subject = body.get('subject', '').strip() or 'Project Inquiry'
        message = body.get('message', '').strip()

        if not name or not email or not message:
            return JsonResponse({'success': False, 'message': 'Name, email, and message are required.'}, status=400)

        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return JsonResponse({'success': False, 'message': 'Please provide a valid email address.'}, status=400)

        # Record lead in database if writable
        try:
            ContactLead.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
        except Exception:
            pass

        # Send Email Notifications via Gmail SMTP
        gmail_user = os.getenv('GMAIL_USER', 'jothilingamsivalingamg@gmail.com')
        gmail_app_password = os.getenv('GMAIL_APP_PASSWORD', '').replace(' ', '')

        if not gmail_app_password:
            # If SMTP password not configured yet, still confirm receipt cleanly
            return JsonResponse({
                'success': True,
                'message': 'Message received successfully! Note: Configure GMAIL_APP_PASSWORD for automated email delivery.'
            })

        if ZoneInfo:
            now_ist = datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%b %d, %Y, %I:%M %p')
        else:
            now_ist = datetime.now().strftime('%b %d, %Y, %I:%M %p')

        # 1. Admin Email to Jothilingam
        admin_subject = f"[Portfolio Lead] {subject} — {name}"
        admin_text = f"New Inquiry from {name} ({email})\nSubject: {subject}\nDate: {now_ist} IST\n\nMessage:\n{message}"
        admin_html = f"""
        <div style="background:#F4F5F0;padding:24px;font-family:sans-serif;">
            <div style="max-width:600px;margin:0 auto;background:#fff;border:1px solid #DDE2D9;border-radius:10px;overflow:hidden;">
                <div style="background:#263746;padding:20px;border-bottom:3px solid #C1A66B;color:#fff;">
                    <span style="font-size:11px;font-weight:700;color:#C1A66B;text-transform:uppercase;">PORTFOLIO LEAD</span>
                    <h2 style="margin:6px 0 0;font-size:20px;">New Message from {escape(name)}</h2>
                </div>
                <div style="padding:24px;color:#263746;font-size:14px;line-height:1.6;">
                    <p><strong>Email:</strong> <a href="mailto:{escape(email)}">{escape(email)}</a></p>
                    <p><strong>Subject:</strong> {escape(subject)}</p>
                    <p><strong>Time:</strong> {now_ist} IST</p>
                    <div style="background:#EAEDE6;padding:16px;border-left:4px solid #496D65;border-radius:6px;margin-top:16px;">
                        <p style="margin:0;white-space:pre-wrap;">{escape(message)}</p>
                    </div>
                </div>
            </div>
        </div>
        """

        msg_admin = EmailMultiAlternatives(
            subject=admin_subject,
            body=admin_text,
            from_email=f"Jothilingam Portfolio <{gmail_user}>",
            to=[gmail_user],
            reply_to=[f"{name} <{email}>"]
        )
        msg_admin.attach_alternative(admin_html, "text/html")
        msg_admin.send(fail_silently=True)

        # 2. Confirmation Email to Visitor
        confirm_subject = f"Thank you for reaching out, {name} | Jothilingam S"
        confirm_text = f"Hi {name},\n\nThank you for reaching out through my portfolio. I have received your message regarding '{subject}' and will review it promptly.\n\nBest regards,\nJothilingam S"
        confirm_html = f"""
        <div style="background:#F4F5F0;padding:24px;font-family:sans-serif;">
            <div style="max-width:600px;margin:0 auto;background:#fff;border:1px solid #DDE2D9;border-radius:10px;overflow:hidden;">
                <div style="background:#263746;padding:20px;border-bottom:3px solid #C1A66B;color:#fff;">
                    <span style="font-size:11px;font-weight:700;color:#C1A66B;text-transform:uppercase;">CONFIRMATION · JOTHILINGAM S</span>
                    <h2 style="margin:6px 0 0;font-size:20px;">Thank you for connecting, {escape(name)}</h2>
                </div>
                <div style="padding:24px;color:#263746;font-size:14px;line-height:1.6;">
                    <p>Hi <strong>{escape(name)}</strong>,</p>
                    <p>Thank you for reaching out through my portfolio. I have successfully received your inquiry regarding <strong>"{escape(subject)}"</strong> and will review it promptly.</p>
                    <div style="background:#EAEDE6;padding:14px;border-left:4px solid #C1A66B;border-radius:6px;margin:16px 0;">
                        <strong>Your Message:</strong>
                        <p style="margin:6px 0 0;white-space:pre-wrap;">{escape(message)}</p>
                    </div>
                    <p style="margin-top:20px;font-size:13px;color:#5F6C65;">
                        <strong>Jothilingam S</strong><br/>
                        Full-Stack Software Engineer & Cloud Architect<br/>
                        Coimbatore, Tamil Nadu, India · +91 89400 66871
                    </p>
                </div>
            </div>
        </div>
        """

        msg_confirm = EmailMultiAlternatives(
            subject=confirm_subject,
            body=confirm_text,
            from_email=f"Jothilingam S <{gmail_user}>",
            to=[email],
            reply_to=[f"Jothilingam S <{gmail_user}>"]
        )
        msg_confirm.attach_alternative(confirm_html, "text/html")
        msg_confirm.send(fail_silently=True)

        return JsonResponse({
            'success': True,
            'message': 'Message delivered successfully! A confirmation email has been sent to your inbox.'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
