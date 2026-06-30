import io
import json
import os
import qrcode
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .wedding_data import WEDDING
from .mongo_db import verify_user, get_setting, save_setting


def _gallery_photos(type_, defaults):
    result = list(defaults)
    for i in range(1, len(defaults) + 1):
        for ext in ('.jpg', '.jpeg', '.png', '.webp'):
            path = os.path.join('media', 'photos', f'gallery_{type_}_{i}{ext}')
            if os.path.exists(path):
                result[i - 1] = f'/media/photos/gallery_{type_}_{i}{ext}'
                break
    return result


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
        {'icon': '🕐', 'label': 'Muhurtham', 'val': get_setting('hero_muhu_muhurtham', w['muhurtham_time'])},
        {'icon': '⭐', 'label': 'Nakshatra',  'val': get_setting('hero_muhu_nakshatra', w['nakshatra'])},
        {'icon': '🌙', 'label': 'Tithi',      'val': get_setting('hero_muhu_tithi', w['tithi'])},
        {'icon': '📍', 'label': 'Venue',      'val': get_setting('hero_muhu_venue', w['venue']['name'])},
    ]
    groom, bride = apply_name_overrides(w['groom'], w['bride'])
    context = {
        'w': w,
        'groom': groom,
        'bride': bride,
        'venue': w['venue'],
        'events': w['events'],
        'youtube': {
            **w['youtube'],
            'video_id':   get_setting('yt_video_id',    w['youtube']['video_id']),
            'embed_url':  get_setting('yt_embed_url',   w['youtube']['embed_url']),
            'channel_url':get_setting('yt_channel_url', w['youtube']['channel_url']),
            'channel_name':get_setting('yt_channel_name',w['youtube']['channel_name']),
            'live_date':  get_setting('yt_live_date',   w['youtube']['live_date']),
        },
        'rsvp': w['rsvp'],
        'quick_links': quick_links,
        'muhurtham_items': muhurtham_items,
        'wedding_date_iso': w['wedding_date_iso'],
        'bride_groom_photos': list(zip(_gallery_photos('couple', w['bride_groom_photos']), w['photo_placeholder_colors']['couple'])),
        'family_photos': list(zip(_gallery_photos('family', w['family_photos']), w['photo_placeholder_colors']['family'])),
        'is_dashboard': True,
        'admin_username': request.session.get('admin_username', 'admin'),
        'overlay_text': get_setting('overlay_text', 'ॐ శుభ వివాహ వేడుక ॐ'),
        'hero_tagline': get_setting('hero_tagline', "We're Getting Married"),
        'hero_invite':  get_setting('hero_invite', "Together with our families,\nwe request the honour of your presence\nto celebrate our wedding ceremony."),
        'hero_date':    get_setting('hero_date', w['wedding_date']),
        'hero_city':    get_setting('hero_city', w['wedding_city']),
        'hero_venue':        get_setting('hero_venue', w['venue']['name']),
        'hero_sacred_quote': get_setting('hero_sacred_quote', w['sacred_quote']),
        'hero_hashtag':      get_setting('hero_hashtag', w['hashtag']),
        'wedding_date_iso':  get_setting('hero_countdown_date', w['wedding_date_iso']),
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
    import qrcode.image.svg as qr_svg
    base_url = request.build_absolute_uri('/preview/')
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(base_url)
    qr.make(fit=True)
    factory = qr_svg.SvgPathFillImage
    img = qr.make_image(image_factory=factory)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode('utf-8')
    # Apply gold fill color
    svg = svg.replace('fill:#000000', 'fill:#D4A017').replace('fill="black"', 'fill="#D4A017"')
    svg = svg.replace('<svg ', '<svg style="background:#060E24;" ')
    return HttpResponse(svg, content_type='image/svg+xml')


@login_required
def save_names(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        groom_name = data.get('groom_name', '').strip()
        bride_name = data.get('bride_name', '').strip()
        for key in ['overlay_text','hero_tagline','hero_invite','hero_date','hero_city','hero_venue','hero_sacred_quote','hero_countdown_date','hero_hashtag',
                    'hero_muhu_muhurtham','hero_muhu_nakshatra','hero_muhu_tithi','hero_muhu_venue',
                    'fam_groom_name','fam_groom_father','fam_groom_mother','fam_groom_city',
                    'fam_bride_name','fam_bride_father','fam_bride_mother','fam_bride_city',
                    'yt_video_id','yt_embed_url','yt_channel_url','yt_channel_name','yt_live_date']:
            val = data.get(key, '').strip()
            if val:
                save_setting(key, val)
        if groom_name:
            save_setting('groom_display_name', groom_name)
        if bride_name:
            save_setting('bride_display_name', bride_name)
        return HttpResponse('{"ok":true}', content_type='application/json')
    return HttpResponse('{"ok":false}', content_type='application/json', status=400)


@login_required
def upload_photo(request):
    if request.method == 'POST':
        role = request.POST.get('role', '').strip().lower()
        import re
        valid_gallery = bool(re.match(r'^gallery_(couple|family)_\d+$', role))
        if role not in ('groom', 'bride', 'couple', 'couple_video') and not valid_gallery:
            return HttpResponse('{"ok":false,"error":"invalid role"}', content_type='application/json', status=400)
        f = request.FILES.get('photo')
        if not f:
            return HttpResponse('{"ok":false,"error":"no file"}', content_type='application/json', status=400)
        ext = os.path.splitext(f.name)[1].lower() or '.jpg'
        save_path = os.path.join('media', 'photos', f'{role}{ext}')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        url = f'/media/photos/{role}{ext}'
        save_setting(f'{role}_photo_ext', ext)
        return HttpResponse(f'{{"ok":true,"url":"{url}"}}', content_type='application/json')
    return HttpResponse('{"ok":false}', content_type='application/json', status=400)
