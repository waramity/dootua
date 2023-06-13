from flask import (render_template, Blueprint, g, redirect,
                   request, current_app, abort, url_for, jsonify, make_response)

from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import Social, Gender, Passion, User, UserSocial, ProfileImage, Location, Preferences
from app.features.auth import render_picture
import names
import random
import datetime, pytz
import uuid
import os
from faker import Faker


management = Blueprint('management', __name__, template_folder='templates', url_prefix='/<lang_code>')

# Multiligual Start
@management.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

@management.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')

@management.before_request
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

fake = Faker()
Faker.seed(0)

def destroy_db():
    db.drop_all()

def create_db():
    db.create_all()

def social_generator():
    social_names = ['google', 'facebook', 'twitter', 'apple']

    for name in social_names:
        social = Social(
            name=name
        )
        db.session.add(social)

    db.session.commit()

# gender_names = ['Man', 'Woman', 'Agender', 'Androgyne', 'Androgynous', 'Bigender', 'Female to male', 'Gender fluid', 'Gender nonconforming', 'Gender questioning', 'Gender variant', 'Genderqueer', 'Male to female', 'Trans', 'Trans man', 'Trans person', 'Trans woman', 'Transfeminine', 'Transgender' , 'Transgender female', 'Transgender male', 'Transgender man', 'Transgender person', 'Transgender woman', 'Transmasculine', 'Transsexual', 'Transsexual female', 'Transsexual male', 'Transsexual man', 'Transsexual person', 'Transsexual woman', 'Two-spirit', 'Neither', 'Neutrois', 'Non-binary', 'Other', 'Pangender']

gender_names = ['Man', 'Woman']

def gender_generator():
    for name in gender_names:
        gender = Gender(
            name=name
        )
        db.session.add(gender)

    db.session.commit()

# def sexual_orientation_generator():
#     sexual_orientation_names = ['Straight', 'Gay', 'Lesbian', 'Bisexual', 'Asexual', 'Demisexual', 'Pansexual', 'Queer', 'Questioning']
#
#     for name in sexual_orientation_names:
#         sexual_orientation = SexualOrientation(
#             name=name
#         )
#         db.session.add(sexual_orientation)
#
#     db.session.commit()

def passion_generator():
    passion_names = ['Cycling', 'Outdoors', 'Walking', 'Cooking', 'Working out', 'Athlete', 'Craft Beer', 'Writer', 'Politics', 'Climbing', 'Foodie', 'Art', 'Karaoke', 'Yoga', 'Blogging', 'Disney', 'Surfing', 'Soccer', 'Dog lover', 'Cat lover', 'Movies', 'Swimming', 'Hiking', 'Running', 'Music', 'Fashion', 'Vlogging', 'Astrology', 'Coffee', 'Instagram', 'DIY', 'Board Games', 'Environmentalism', 'Dancing', 'Volunteering', 'Trivia', 'Reading', 'Tea', 'Language Exchange', 'Shopping', 'Wine', 'Travel']

    for name in passion_names:
        passion = Passion(
            name=name
        )
        db.session.add(passion)

    db.session.commit()

# random datetime between two dates
def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)
# end random datetime between two dates

def user_generator(gender):
    unique_id = uuid.uuid4().hex
    while User.query.filter_by(id=unique_id).first():
        unique_id = uuid.uuid4().hex

    user_social = UserSocial(
        social_auth_id=unique_id,
        social_id=Social.query.filter_by(name='google').first().id,
        user_id=unique_id
    )

    if gender == "male":
        path = "./app/test/profile_images/male/"
        gender_id = Gender.query.filter_by(id=1).first().id
    else:
        path = "./app/test/profile_images/female/"
        gender_id = Gender.query.filter_by(id=2).first().id

    files = os.listdir(path)
    file = random.choice(files)
    file = open(path + file, 'rb')

    data = file.read()
    render_file = render_picture(data)

    profile_images = []
    profile_image = ProfileImage(name=file.name, data=data, rendered_data=render_file, user_id=unique_id, uploaded_date=datetime.datetime.now(pytz.timezone('UTC')))
    profile_images.append(profile_image)
    db.session.add(profile_image)

    fake_location = fake.local_latlng(country_code="TH")
    # location = Location.query.filter(Location.latitude.like(float(fake_location[0])), Location.longitude.like(float(fake_location[1]))).first()

    # if location is None:
    #     location = Location(latitude=float(fake_location[0]), longitude=float(fake_location[1]))
    #     db.session.add(location)

    location = Location(latitude=float(fake_location[0]), longitude=float(fake_location[1]), user_id=unique_id)
    db.session.add(location)

    preferences = Preferences(
        user_id=unique_id,
        showmes=random.choices(Gender.query.all(), k=1),
    )
    db.session.add(preferences)

    print(preferences.showmes)
    user = User(
        id=unique_id,
        registered_on=datetime.datetime.now(),
        user_social=user_social,
        given_name = names.get_first_name(),
        birthday=random_date(datetime.datetime.strptime('1/1/1980', '%m/%d/%Y'), datetime.datetime.strptime('1/1/2001', '%m/%d/%Y')),
        gender_id=gender_id,
        # showmes=random.choices(Gender.query.all(), k=2),
        passions=random.choices(Passion.query.all(), k=3),
        profile_images=profile_images,
        last_location=location,
        preferences=preferences
    )

    print(user)
    # print(Gender.query.filter_by(name=random.choice(gender_names)).first())
    # print(showmes)
    # print(passions)
    # print(profile_images)

    db.session.add(user)
    print(user.registered_on)
    db.session.commit()

@management.route('/bypass-user-login/<user_id>')
def bypass_user_login(user_id):
    user = User.query.filter_by(id=user_id).first()
    login_user(user)
    return redirect(url_for('main.app'))
