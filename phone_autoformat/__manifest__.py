{
    'name': 'Phone Auto Format',
    'summary': 'Automatically format phone numbers on contacts, with a format chosen in Settings',
    'version': '20.0.1.1.1',
    'category': 'Tools',
    'author': 'Syed Sameed Zafar',
    'maintainer': 'Syed Sameed Zafar',
    'website': 'https://syed-sameed-zafar.vercel.app/',
    'license': 'LGPL-3',
    'depends': ['base', 'contacts', 'phone_validation'],
    'external_dependencies': {'python': ['phonenumbers']},
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/screenshot1.png',
        'static/description/screenshot2.png',
        'static/description/screenshot3.png',
        'static/description/screenshot4.png',
    ],
    'installable': True,
    'application': False,
}
