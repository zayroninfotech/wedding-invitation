from django.shortcuts import render
from .wedding_data import WEDDING


def home(request):
    w = WEDDING

    quick_links = [
        {'href': '#family',  'emoji': '👨‍👩‍👧', 'label': 'Family'},
        {'href': '#events',  'emoji': '📅',                 'label': 'Events'},
        {'href': '#gallery', 'emoji': '📸',                 'label': 'Gallery'},
        {'href': '#live',    'emoji': '▶',                  'label': 'Live Stream'},
        {'href': '#rsvp',    'emoji': '💌',                 'label': 'RSVP'},
    ]

    muhurtham_items = [
        {'icon': '🕐', 'label': 'Muhurtham', 'val': w['muhurtham_time']},
        {'icon': '⭐', 'label': 'Nakshatra',  'val': w['nakshatra']},
        {'icon': '🌙', 'label': 'Tithi',      'val': w['tithi']},
        {'icon': '📍', 'label': 'Venue',      'val': w['venue']['name']},
    ]

    context = {
        'w':                 w,
        'groom':             w['groom'],
        'bride':             w['bride'],
        'venue':             w['venue'],
        'events':            w['events'],
        'youtube':           w['youtube'],
        'rsvp':              w['rsvp'],
        'quick_links':       quick_links,
        'muhurtham_items':   muhurtham_items,
        'wedding_date_iso':  w['wedding_date_iso'],
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
