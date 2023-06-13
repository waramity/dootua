from flask import (render_template, Blueprint, g, redirect,
                   request, current_app, abort, url_for, jsonify, make_response, session)
from flask_babel import _, refresh
from flask_login import login_required, current_user
from flask_socketio import send, emit, join_room, leave_room
import geocoder
from app import app, db, socketio
from app.models import Location, User, Preferences, Gender, Likes, Matches, Message

from math import radians, cos, sin, asin, sqrt
import random
import datetime, time, pytz

from dateutil.relativedelta import relativedelta

import math
from sqlalchemy import func, and_

import uuid
import json

main = Blueprint('main', __name__, template_folder='templates', url_prefix='/<lang_code>' )

# Multiligual Start
@main.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

@main.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')

@main.before_request
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

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.given_name is None:
            return redirect(url_for('auth.create_profile'))
        elif current_user.geolocation_permission == False or current_user.geolocation_permission == None:
            return redirect(url_for('auth.geolocation'))
        else:
            return redirect(url_for('main.app'))
    #     return '<a class="button" href="/login">Google Login</a>'
    return render_template('main/index.html', title=_('Dootua - คู่ชีวิตที่คุณตามหา'))

def get_geolocation():
    ip = geocoder.ip('me')
    location = Location.query.filter_by(user_id=current_user.id).first()
    location.latitude = float(ip.lat)
    location.longitude = float(ip.lng)
    current_user.last_location = location
    db.session.commit()


@main.route('/app')
@login_required
def app():
    get_geolocation()
    # if location is None:
    #     location = Location(latitude=float(ip.lat), longitude=float(ip.lng))
    #     db.session.add(location)
    #     db.session.commit()
    #     location = Location.query.filter(Location.latitude.like(ip.lat), Location.longitude.like(ip.lng)).first()
    #     current_user.last_location_id = location.id
    #     db.session.commit()
    # else:
    #     current_user.last_location_id = location.id
    #     db.session.commit()
    return render_template('main/match.html', title=_('Dootua - คู่ชีวิตที่คุณตามหา'))

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

def calculate_age(birthday):
    today = datetime.date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

def distanceMath(lat1, lat2, lon1, lon2):
    distance = math.acos(math.sin(math.radians(lat1))*math.sin(math.radians(lat2))) + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.cos(math.radians(lon1)-math.radians(lon2))
    return distance

@main.route('/get-user-based-on-preferences', methods=['POST'])
@login_required
def get_user_based_on_preferences():
    # if request.method == 'POST' and request.json is not None:
    if request.method == 'POST':
        datetime_now = datetime.datetime.now()
        preferences = Preferences.query.filter_by(user_id=current_user.id).first()
        start_datetime = datetime_now - relativedelta(years=preferences.end_age)
        end_datetime = datetime_now - relativedelta(years=preferences.start_age)
        # print(current_user.preferences.showmes)
        # users = [i.serialize for i in User.query.join(User.preferences).join(User.last_location).filter(User.id!=current_user.id, User.birthday.between(start_datetime, end_datetime), User.gender_id.in_(gender.id for gender in current_user.preferences.showmes), distanceMath(current_user.last_location.latitude, float(Location.latitude), current_user.last_location.longitude, float(Location.longitude)) <= Preferences.distance).all()]
        users = [i.serialize for i in User.query.join(User.last_location).filter(User.id!=current_user.id, User.birthday.between(start_datetime, end_datetime), User.gender_id.in_(gender.id for gender in current_user.preferences.showmes), func.acos(func.sin(func.radians(current_user.last_location.latitude)) * func.sin(func.radians(Location.latitude)) + func.cos(func.radians(current_user.last_location.latitude)) * func.cos(func.radians(Location.latitude)) * func.cos(func.radians(Location.longitude) - (func.radians(current_user.last_location.longitude)))) * 6371 <= preferences.distance, User.id.not_in(like.to_user_id for like in current_user.likes)).all()]
        # users = [i.serialize for i in User.query.join(User.last_location, User.likes).filter(User.id!=current_user.id, User.birthday.between(start_datetime, end_datetime), User.gender_id.in_(gender.id for gender in current_user.preferences.showmes), func.acos(func.sin(func.radians(current_user.last_location.latitude)) * func.sin(func.radians(Location.latitude)) + func.cos(func.radians(current_user.last_location.latitude)) * func.cos(func.radians(Location.latitude)) * func.cos(func.radians(Location.longitude) - (func.radians(current_user.last_location.longitude)))) * 6371 <= preferences.distance, and_(Likes.from_user_id!=current_user.id, Likes.to_user_id!=User.id)).all()]
        # print(users)
        random.shuffle(users)
        current_user_last_location = Location.query.filter_by(user_id=current_user.id).first()
        for user in users:
            distance = haversine(current_user_last_location.latitude, current_user_last_location.longitude, user['last_location']['latitude'], user['last_location']['longitude'])
            del user['last_location']
            user['distance'] = distance

        # users = User.query.filter(User.id.in_(like.to_user_id for like in current_user.likes)).all()
        # print(users)
        # print(current_user.likes)
        # for i in User.query.all():
        #     print(i.serialize())
            # print(i)
            # print(i.to_dict(only=('id', 'given_name', 'birthday', 'gender')))
        # print(User.query.all())
        # print([i.serialize for i in User.query.all()])
        return make_response(jsonify(users), 200)
        # return jsonify(users), 201

@main.route('/get-user-preferences', methods=['POST'])
@login_required
def get_user_preferences():
    if request.method == 'POST':
        preferences = Preferences.query.filter_by(user_id=current_user.id).first().serialize
        # users = [i.serialize for i in User.query.all()]
        # current_user_last_location = Location.query.filter_by(user_id=current_user.id).first()
        # for user in users:
        #     distance = haversine(current_user_last_location.latitude, current_user_last_location.longitude, user['last_location']['latitude'], user['last_location']['longitude'])
        #     del user['last_location']
        #     user['distance'] = distance
        return make_response(jsonify(preferences), 200)

@main.route('/save-changes-preferences', methods=['POST'])
@login_required
def save_changes_preferences():
    # print(request.json)
    if request.method == 'POST' and request.json is not None:

        preferences = Preferences.query.filter_by(user_id=current_user.id).first()
        if request.json['start_age'] < 20 or request.json['start_age'] > 65:
            request.json['start_age'] = 20
        if request.json['end_age'] < 20 or request.json['end_age'] > 65:
            request.json['end_age'] = 65
        if request.json['distance'] < 10 or request.json['distance'] > 700:
            request.json['distance'] = 700

        showmes = []
        for gender_id in request.json['showmes']:
            if isinstance(gender_id,int) and gender_id > 0 and gender_id < 3:
                showmes.append(Gender.query.filter_by(id=gender_id).first())
            else:
                continue

        if showmes == []:
            showmes.append(Gender.query.filter_by(id=1).first())

        # print(preferences.showmes)
        # print(showmes)

        preferences.start_age = request.json['start_age']
        preferences.end_age = request.json['end_age']
        preferences.distance = request.json['distance']
        preferences.showmes = showmes

        db.session.commit()

        preferences = Preferences.query.filter_by(user_id=current_user.id).first().serialize
        # users = [i.serialize for i in User.query.all()]
        # current_user_last_location = Location.query.filter_by(user_id=current_user.id).first()
        # for user in users:
        #     distance = haversine(current_user_last_location.latitude, current_user_last_location.longitude, user['last_location']['latitude'], user['last_location']['longitude'])
        #     del user['last_location']
        #     user['distance'] = distance
        return make_response(jsonify(preferences), 200)

def random_uuid(model):
    unique_id = uuid.uuid4().hex
    while model.query.filter_by(id=unique_id).first():
        unique_id = uuid.uuid4().hex
    return unique_id

@main.route('/update-like', methods=['POST'])
@login_required
def update_like():
    if request.method == 'POST' and request.json is not None:
        result = {}
        # print(request.json["res_user_id"])
        from_user_like = Likes.query.filter(Likes.from_user_id==str(current_user.id), Likes.to_user_id==str(request.json["res_user_id"])).first()
        # print(Likes.query.filter(Likes.to_user_id=="7215c992b5c945bfb09707c31f068f42").first())
        # print(len(Likes.query.all()))
        # if like is None:
        #     like = Likes.query.filter(Likes.req_user_id==request.json["res_user_id"], Likes.res_user_id==current_user.id).first()
        # print(like)
        if from_user_like is None:
            # print(request.json["res_user_id"])
            from_user_like = Likes(id=random_uuid(Likes), from_user_id=current_user.id, to_user_id=str(request.json["res_user_id"]), like=bool(request.json["like"]), created_date=datetime.datetime.now(pytz.timezone('UTC')))
            # print(like)
            current_user.likes.append(from_user_like)
            db.session.add(from_user_like)
            print(len(current_user.likes))
            if from_user_like.like is True:
                to_user_like = Likes.query.filter(Likes.from_user_id==str(request.json["res_user_id"]), Likes.to_user_id==current_user.id, Likes.like==True).first()
                print(to_user_like)
                if to_user_like is not None:
                    match = Matches(id=random_uuid(Matches), sender_id=current_user.id, recipient_id=str(request.json["res_user_id"]), created_date=datetime.datetime.now(pytz.timezone('UTC')))
                    db.session.add(match)
                    current_user.matches.append(match)
                    to_user = User.query.filter_by(id=str(request.json["res_user_id"])).first()
                    # to_user_match = Matches(id=random_uuid(Matches), from_user_id=str(request.json["res_user_id"]), to_user_id=current_user.id)
                    to_user.matches.append(match)
                    # db.session.add(to_user_match)
                    db.session.commit()
                    print(current_user.matches)
                    result['result'] = 'Match'
                    result.update({'match_id': match.id, 'user_id': to_user.id, 'given_name': to_user.given_name, 'profile_image_uri': to_user.profile_images[0].rendered_data, 'last_message': {"message": None, "datetime": None}})
                    # result['id'] = to_user.id
                    # result['given_name'] = to_user.given_name,
                    # result['profile_image_uri'] = to_user.profile_images[0].rendered_data,
                    # result['updated_date'] = int(time.mktime(match.updated_date.timetuple())) * 1000
                    return make_response(jsonify(result), 200)

        # like = Likes.query.all()
        #
        # print(like)


            print(current_user.likes)
            db.session.commit()
            result["result"] = "Like"
            return make_response(jsonify(result), 200)

@main.route('/update-dislike', methods=['POST'])
@login_required
def update_dislike():
    if request.method == 'POST' and request.json is not None:
        result = {}
        from_user_like = Likes.query.filter(Likes.from_user_id==str(current_user.id), Likes.to_user_id==str(request.json["res_user_id"])).first()
        if from_user_like is None:
            # print(request.json["res_user_id"])
            from_user_like = Likes(id=random_uuid(Likes), from_user_id=current_user.id, to_user_id=str(request.json["res_user_id"]), like=bool(request.json["like"]), created_date=datetime.datetime.now(pytz.timezone('UTC')))
            if from_user_like.like is False:
                # print(like)
                current_user.likes.append(from_user_like)
                db.session.add(from_user_like)
                db.session.commit()
                print(len(current_user.likes))
                result["result"] = "Dislike"
                return make_response(jsonify(result), 200)

# @main.route('/get-matches/<int:pagination>', methods=['POST'])
# @login_required
# def get_matches(pagination):
#     matches = [match.serialize for match in Matches.query.filter((Matches.sender_id==current_user.id) | (Matches.recipient_id==current_user.id)).order_by(Matches.updated_date.desc()).all()]
#     return make_response(jsonify(matches), 200)

def stringifyDateTime(dateTimeObject):
    if isinstance(dateTimeObject, datetime.datetime):
        # print(dateTimeObject.__str__())
        return dateTimeObject.__str__()

@socketio.on("userConnected")
@login_required
def userConnected():
    session.pop("current_chat", None)
    # join_room(session.get("user").get("id"))
    join_room(current_user.id)
    # chatRooms = db.session.query(ChatRoom).filter((ChatRoom.senderID == session.get("user").get("id")) | (ChatRoom.recipientID == session.get("user").get("id"))).all()
    # matches = [match.serialize for match in Matches.query.filter((Matches.sender_id==current_user.id) | (Matches.recipient_id==current_user.id)).order_by(Matches.updated_date.desc()).all()]
    # matches = Matches.query.filter((Matches.sender_id==current_user.id) | (Matches.recipient_id==current_user.id)).order_by(Matches.updated_date.desc()).all()
    matches = Matches.query.filter((Matches.sender_id==current_user.id) | (Matches.recipient_id==current_user.id)).all()

    all_chats = []
    for match in matches:
        if match.sender_id == current_user.id:
            user_id = match.recipient_id
        else:
            user_id = match.sender_id

        recipient_user = User.query.filter((User.id == user_id)).first()
        last_message = Message.query.filter((Message.match_id == match.id)).order_by(Message.created_date.desc()).first()
        message = None
        if last_message:
            print(last_message.created_date)
            message = {"message": last_message.message, "created_date": json.dumps(last_message.created_date, default=stringifyDateTime)}
        else:
            message = {"message": None, "created_date": None}
        if recipient_user:
            all_chats.append({'match_id': match.id, 'user_id': user_id, 'given_name': recipient_user.given_name, 'last_message': message, 'profile_image_uri': recipient_user.profile_images[0].rendered_data})
    socketio.emit("chatRooms", all_chats, room=current_user.id)

@socketio.on("changeChat")
def changeChat(user_id, match_id):
    session["current_chat"] = user_id
    print(session.get("current_chat"))
    messages = Message.query.filter((Message.match_id == match_id)).all()
    recipient_user = User.query.filter((User.id == user_id)).first()
    payload = {"recipient_id": user_id, "profile_image_uri": recipient_user.profile_images[0].rendered_data, "all_messages": []}
    for message in messages:
        message_type = "receivedMessage"
        if current_user.id == message.sender_id:
            message_type = "sentMessage"
        payload['all_messages'].append({"match_id": match_id, "message_type": message_type, "created_date": json.dumps(message.created_date, default=stringifyDateTime), "message": message.message})
        # print(message.created_date)
    socketio.emit("displayAllMessages", payload, room=current_user.id)
    print(session.get("current_chat"))

@socketio.on("message")
def message(form):
    # print(form)
    match_id = form['match_id']
    recipient_id = form['recipient_id']
    message = form['message']

    print(session.get("current_chat"))
    user = User.query.filter(User.id == recipient_id).first()
    if not user:
        flash("No such account exists.")
        return redirect(url_for("main.app"))
    new_message = Message(id=random_uuid(Message), match_id=match_id, sender_id=current_user.id, message=message, created_date=datetime.datetime.now(pytz.timezone('UTC')))
    # print(datetime.datetime.now(pytz.timezone('Asia/Bangkok')))
    db.session.add(new_message)
    db.session.commit()

    socketio.emit("sentMessage", {"match_id": match_id, "recipient_id": recipient_id, "sender_id": current_user.id, "message": message, "created_date": json.dumps(new_message.created_date, default=stringifyDateTime)}, room=current_user.id)
    socketio.emit("receivedMessage", {"match_id": match_id, "recipient_id": recipient_id, "sender_id": current_user.id, "message": message, "created_date": json.dumps(new_message.created_date, default=stringifyDateTime), "given_name": current_user.given_name, "profile_image_uri": current_user.profile_images[0].rendered_data}, room=recipient_id)

@socketio.on("receivedMessage")
def receivedMessage(data):
    print('test')
    print(data['sender_id'])
    print(session.get("current_chat"))
    # print(current_user.id)
    # print(current_user.given_name)
    print(data["sender_id"] == session.get("current_chat"))
    if data["sender_id"] == session.get("current_chat"):
        socketio.emit("displayReceivedMessage", data, room=data["recipient_id"])
    else:
        socketio.emit("displayNotification", data, room=data["recipient_id"])
