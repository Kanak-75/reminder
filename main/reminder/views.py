from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def index(request):
    return render(request, 'index.html')

def authorize(request):
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri='http://localhost:8000/oauth2callback'
    )
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    request.session['state'] = state
    return redirect(authorization_url)

def oauth2callback(request):
    state = request.session['state']
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        state=state,
        redirect_uri='http://localhost:8000/oauth2callback'
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    service = build('calendar', 'v3', credentials=credentials)
    events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return render(request, 'index.html', {'events': events})

def send_notification(request):
    send_mail(
        subject='Reminder: Upcoming Meeting',
        message='This is a reminder for your upcoming meeting.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['your_email@gmail.com'],
        fail_silently=False,
    )
    return redirect('index')
