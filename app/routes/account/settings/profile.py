
from app.common.constants.regexes import DISCORD_USERNAME, URL
from app.common.database.repositories import users

from flask_login import login_required, current_user
from flask import Blueprint, request, redirect
from datetime import datetime

from . import account
from . import avatar

import utils
import app

router = Blueprint('profile-settings', __name__)
router.register_blueprint(account.router, url_prefix='/profile')
router.register_blueprint(avatar.router, url_prefix='/profile')

@router.get('/profile')
@login_required
def profile_settings():
    return utils.render_template(
        'settings/profile.html',
        css='settings.css'
    )

def check_account_status() -> str | None:
    if current_user.restricted:
        return utils.render_template(
            'settings/profile.html',
            css='settings.css',
            error='Your account was restricted.'
        )

    if current_user.silence_end and \
       current_user.silence_end > datetime.now():
            return utils.render_template(
                'settings/profile.html',
                css='settings.css',
                error='Your account was silenced.'
            )

    if not current_user.activated:
        return utils.render_template(
            'settings/profile.html',
            css='settings.css',
            error='Your account is not activated.'
        )

@router.post('/profile')
@login_required
def update_profile_settings():
    interests = request.form.get('interests') or None
    location = request.form.get('location') or None
    website = request.form.get('website') or None
    discord = request.form.get('discord') or None
    twitter = request.form.get('twitter') or None

    if discord != None:
        discord = discord.removeprefix('@')

        if not DISCORD_USERNAME.match(discord):
            return utils.render_template(
                'settings/profile.html',
                css='settings.css',
                error='Invalid discord username. Please try again!'
            )

    if interests != None and len(interests) > 30:
        return utils.render_template(
            'settings/profile.html',
            css='settings.css',
            error='Please keep your interests short!'
        )

    if location != None and len(location) > 30:
        return utils.render_template(
            'settings/profile.html',
            css='settings.css',
            error='Please keep your location short!'
        )

    if twitter != None and len(twitter) > 64:
        return utils.render_template(
            'settings/profile.html',
            css='settings.css',
            error='Please type in a valid twitter handle or url!'
        )

    if website != None and len(website) > 64:
        return utils.render_template(
            'settings/profile.html',
            css='settings.css',
            error='Please keep your website url short!'
        )

    if website != None and not URL.match(website):
        return utils.render_template(
            'settings/profile.html',
            css='settings.css',
            error='Please enter in a valid url!'
        )

    if error := check_account_status():
        return error

    updates = {
        'userpage_interests': interests,
        'userpage_location': location,
        'userpage_website': website,
        'userpage_discord': discord,
        'userpage_twitter': f'https://twitter.com/{app.get_handle(twitter)}' \
            if twitter else None
    }

    # Update user object
    current_user.__dict__.update(updates)

    # Update database
    users.update(
        current_user.id,
        updates
    )

    return utils.render_template(
        'settings/profile.html',
        css='settings.css',
        info='Successfully updated profile.'
    )

@router.post('/profile/userpage')
@login_required
def update_userpage():
    if (bbcode := request.form.get('bbcode')) is None:
        return redirect('/account/settings/profile')

    user_id = request.form.get('user_id', type=int)

    if current_user.id != user_id and not current_user.is_admin:
        return redirect('/account/settings/profile')

    if error := check_account_status():
        return error

    # Update database
    users.update(
        user_id,
        {'userpage_about': bbcode}
    )

    # Update user object
    current_user.userpage_about = bbcode

    if user_id != current_user.id:
        return redirect(f'/u/{user_id}')

    return redirect('/account/settings/profile#userpage')

@router.post('/profile/signature')
@login_required
def update_signature():
    if (bbcode := request.form.get('bbcode')) is None:
        return redirect('/account/settings/profile')

    user_id = request.form.get('user_id', type=int)

    if current_user.id != user_id and not current_user.is_admin:
        return redirect('/account/settings/profile')

    if error := check_account_status():
        return error

    # Update database
    users.update(
        user_id,
        {'userpage_signature': bbcode}
    )

    # Update user object
    current_user.userpage_signature = bbcode

    if user_id != current_user.id:
        return redirect(f'/u/{user_id}')

    return redirect('/account/settings/profile#signature')
