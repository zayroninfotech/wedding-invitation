import io
import qrcode
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .wedding_data import WEDDING
from .mongo_db import verify_user


def login_required(view_fn):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            return redirect('admin_login')
        return view_fn(request, *args, **kwargs)
    wrapper.__name__ = view_fn.__name__
    return wrapper


def admin_login(request):
    if request.session.get('admin_logged_in'):
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if verify_user(username, password):
            request.session['admin_logged_in'] = True
            request.session['admin_username'] = username.strip().lower()
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'invitation/login.html')


def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')


@login_required
def dashboard(request):
    w = WEDDING
    quick_links = [
        {'href': '#family',  'emoji': '👨‍👩‍👧', 'label': 'Family'},
        {'href': '#events',  'emoji': '📅',      'label': 'Events'},
        {'href': '#gallery', 'emoji': '📸',      'label': 'Gallery'},
        {'href': '#live',    'emoji': '▶',       'label': 'Live Stream'},
        {'href': '#rsvp',    'emoji': '💌',      'label': 'RSVP'},
    ]
    muhurtham_items = [
        {'icon': '🕐', 'label': 'Muhurtham', 'val': w['muhurtham_time']},
        {'icon': '⭐', 'label': 'Nakshatra',  'val': w['nakshatra']},
        {'icon': '🌙', 'label': 'Tithi',      'val': w['tithi']},
        {'icon': '📍', 'label': 'Venue',      'val': w['venue']['name']},
    ]
    context = {
        'w': w,
        'groom': w['groom'],
        'bride': w['bride'],
        'venue': w['venue'],
        'events': w['events'],
        'youtube': w['youtube'],
        'rsvp': w['rsvp'],
        'quick_links': quick_links,
        'muhurtham_items': muhurtham_items,
        'wedding_date_iso': w['wedding_date_iso'],
        'bride_groom_photos': list(zip(w['bride_groom_photos'], w['photo_placeholder_colors']['couple'])),
        'family_photos': list(zip(w['family_photos'], w['photo_placeholder_colors']['family'])),
    }
    return render(request, 'invitation/home.html', context)


def home(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')
    return redirect('dashboard')


def wedding_preview(request):
    w = WEDDING

    quick_links = [
        {'href': '#family',  'emoji': '👨‍👩‍👧', 'label': 'Family'},
        {'href': '#events',  'emoji': '📅',      'label': 'Events'},
        {'href': '#gallery', 'emoji': '📸',      'label': 'Gallery'},
        {'href': '#live',    'emoji': '▶',       'label': 'Live Stream'},
        {'href': '#rsvp',    'emoji': '💌',      'label': 'RSVP'},
    ]

    muhurtham_items = [
        {'icon': '🕐', 'label': 'Muhurtham', 'val': w['muhurtham_time']},
        {'icon': '⭐', 'label': 'Nakshatra',  'val': w['nakshatra']},
        {'icon': '🌙', 'label': 'Tithi',      'val': w['tithi']},
        {'icon': '📍', 'label': 'Venue',      'val': w['venue']['name']},
    ]

    context = {
        'w':                  w,
        'groom':              w['groom'],
        'bride':              w['bride'],
        'venue':              w['venue'],
        'events':             w['events'],
        'youtube':            w['youtube'],
        'rsvp':               w['rsvp'],
        'quick_links':        quick_links,
        'muhurtham_items':    muhurtham_items,
        'wedding_date_iso':   w['wedding_date_iso'],
        'bride_groom_photos': list(zip(
            w['bride_groom_photos'],
            w['photo_placeholder_colors']['couple'],
        )),
        'family_photos': list(zip(
            w['family_photos'],
            w['photo_placeholder_colors']['family'],
        )),
    }
    return render(request, 'invitation/home.html', context)


@login_required
def generate_qr(request):
    base_url = request.build_absolute_uri('/preview/')
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(base_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#D4A017', back_color='#060E24')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return HttpResponse(buf, content_type='image/png')
