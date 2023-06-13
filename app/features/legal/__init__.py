from flask import (render_template, Blueprint, g, redirect,
                   request, current_app, abort, url_for)
from flask_babel import _, refresh
from flask_login import login_required, current_user
from app import app

legal = Blueprint('legal', __name__, template_folder='templates', url_prefix='/<lang_code>' )

# Multiligual Start
@legal.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

@legal.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')

@legal.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = app.url_map.bind('')
        try:
            endpoint, args = adapter.match(
                '/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)

    dfl = request.url_rule.defaults
    if 'lang_code' in dfl:
        if dfl['lang_code'] != request.full_path.split('/')[1]:
            abort(404)
# Multiligual End

@legal.route('/privacy')
def privacy():
    return render_template('legal/privacy.html', title=_('ความเป็นส่วนตัว'))

@legal.route('/terms')
def terms():
    return render_template('legal/terms.html')

@legal.route('/faq')
def faq():
    return render_template('legal/faq.html')

@legal.route('/cookies-policy')
def cookies_policy():
    return render_template('legal/cookies_policy.html')
