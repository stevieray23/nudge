import re

GENERIC_LOCAL = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption',
    'empfang','sekretariat','poststelle','redaktion','webmaster','noreply','no-reply',
    'datenschutz','privacy'}
BAD = {'sentry','usercentrics','cookiebot','google.com','facebook','instagram','linkedin',
    'xing','twitter','bit.ly','lzk','kzvr','kzvs','zaek','aekwl','bezreg','lzkbw',
    'brd.nrw','sozmi.landsh','blzk','bezirksstelle','zahnarztboerse','dentale','domain.com'}

def is_clean(email):
    if not email or '@' not in email: return False
    lo = email.lower()
    local = lo.split('@')[0]
    domain = lo.split('@')[1] if '@' in lo else ''
    if any(x in lo for x in ['.png','.jpg','.svg','data:image']): return False
    if any(x in domain for x in BAD): return False
    if any(x in local for x in BAD): return False
    if local in GENERIC_LOCAL:
        public = ['gmail','yahoo','hotmail','outlook','web.de','t-online.de','gmx.de','aol.com','icloud.com','protonmail','mail.de','freenet.de']
        if any(p in domain for p in public): return False
        # Clinic's own domain = accept
        if domain.endswith('.de') or domain.endswith('.com') or domain.endswith('.net'):
            return True
        return False
    return True

test_emails = [
    ('anmeldung@bilow.de', True),
    ('bornheim@nautilus-praxen.de', True),
    ('dr.sandrabilitas@yahoo.com', True),
    ('contact@cornflowerclinic.co.uk', True),
    ('verwaltung@zahnarztteam-frankfurt.de', True),
    ('zahnaerzte@hauptwache5.de', True),
    ('kzvh@kzvh.de', False),
    ('cgb@stahlberg-partner.de', True),
    ('praxis@dr-mueller.de', True),
    ('hennig@zahnarztpraxis-hennig.de', True),
    ('dr.uta.wolff@gmail.com', True),
    ('tobias.mayer@gmx.de', True),
    ('praxis@alldent.de', False),
    ('info@google.com', False),
    ('datenschutz@blzk.de', False),
    ('annegret.kreuzberger@web.de', True),
    ('termin@fachzahnaerzte.ruhr', True),
    ('info@dentalke.de', False),
    ('praxis@dentalke.de', False),
]

for email, expected in test_emails:
    result = is_clean(email)
    status = 'OK' if result == expected else 'WRONG'
    print(f'{status} [{result}] {email}')
