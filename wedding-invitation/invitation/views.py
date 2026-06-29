import io
import json
import qrcode
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .wedding_data import WEDDING
from .mongo_db import verify_user, get_setting, save_setting


def apply_name_overrides(groom, bride):
    groom = dict(groom)
    bride = dict(bride)
    g = get_setting('groom_display_name')
    b = get_setting('bride_display_name')
    if g:
        groom['first_name'] = g
    if b:
        bride['first_name'] = b
    return groom, bride


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
            return redirect('admin_panel')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'invitation/login.html')


def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')


@login_required
def admin_panel(request):
    w = WEDDING
    context = {
        'w': w,
        'admin_username': request.session.get('admin_username', 'admin'),
    }
    return render(request, 'invitation/admin_panel.html', context)


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
    groom, bride = apply_name_overrides(w['groom'], w['bride'])
    context = {
        'w': w,
        'groom': groom,
        'bride': bride,
        'venue': w['venue'],
        'events': w['events'],
        'youtube': w['youtube'],
        'rsvp': w['rsvp'],
        'quick_links': quick_links,
        'muhurtham_items': muhurtham_items,
        'wedding_date_iso': w['wedding_date_iso'],
        'bride_groom_photos': list(zip(w['bride_groom_photos'], w['photo_placeholder_colors']['couple'])),
        'family_photos': list(zip(w['family_photos'], w['photo_placeholder_colors']['family'])),
        'is_dashboard': True,
        'admin_username': request.session.get('admin_username', 'admin'),
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


@login_required
def save_names(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        groom_name = data.get('groom_name', '').strip()
        bride_name = data.get('bride_name', '').strip()
        if groom_name:
            save_setting('groom_display_name', groom_name)
        if bride_name:
            save_setting('bride_display_name', bride_name)
        return HttpResponse('{"ok":true}', content_type='application/json')
    return HttpResponse('{"ok":false}', content_type='application/json', status=400)
