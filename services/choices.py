SERVICE_CHOICES = [
    ('nail', 'خدمات ناخن'),
    ('lash', 'خدمات مژه'),
    ('facial', 'خدمات فشیال'),
    ('scalp', 'خدمات اسکالپ'),
    ('root_color', 'رنگ ریشه'),
    ('light', 'لایت'),
    ('treatment', 'احیای مو'),
    ('eyebrow', 'اصلاح ابرو'),
    ('wax', 'وکس'),
    ('pedicure', 'پدیکور'),
]

SERVICE_DURATIONS = {
    'nail': 120,
    'lash': 120,
    'facial': 120,
    'scalp': 120,
    'root_color': 120,
    'light': 600,
    'treatment': 300,
    'eyebrow': 20,
    'wax': 30,
    'pedicure': 120,
}

SERVICE_DEPOSITS = {
    'nail': 200_000,
    'lash': 300_000,
    'facial': 300_000,
    'scalp': 300_000,
    'root_color': 300_000,
    'light': 500_000,
    'treatment': 500_000,
    'eyebrow': 100_000,
    'wax': 100_000,
    'pedicure': 300_000,
}
