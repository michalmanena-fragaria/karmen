import bcrypt
from flask import jsonify, request, abort
from flask_cors import cross_origin
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    fresh_jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_current_user,
    decode_token,
)
from server import app
from server.database import users, local_users, api_tokens


def authenticate_base(include_refresh_token):
    data = request.json
    if not data:
        return abort(400)
    username = data.get("username", None)
    password = data.get("password", None)
    if not username or not password:
        return abort(400)

    user = users.get_by_username(username)
    if not user:
        return abort(401)

    local = local_users.get_local_user(user["uuid"])
    if not local:
        return abort(401)
    if not bcrypt.checkpw(password.encode("utf8"), local["pwd_hash"].encode("utf8")):
        return abort(401)

    userdata = dict(user)
    userdata.update(local)
    response = {"access_token": create_access_token(identity=userdata, fresh=True)}
    if include_refresh_token:
        response["refresh_token"] = create_refresh_token(identity=userdata)
    return jsonify(response), 200


# This is intentionally not called login as we might use that for the OAuth process in the future
# This returns a fresh access token and a refresh token
@app.route("/users/me/authenticate", methods=["POST"])
@cross_origin()
def authenticate():
    return authenticate_base(True)


# This returns a fresh access token and no refresh token
@app.route("/users/me/authenticate-fresh", methods=["POST"])
@cross_origin()
def authenticate_fresh():
    return authenticate_base(False)


# This returns a non fresh access token and no refresh token
@app.route("/users/me/authenticate-refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    user = get_current_user()
    if not user:
        return abort(401)

    local = local_users.get_local_user(user["uuid"])
    if not local:
        return abort(401)
    userdata = dict(user)
    userdata.update(local)
    return jsonify({"access_token": create_access_token(identity=userdata)}), 200


@app.route("/users/me/probe", methods=["GET"])
@cross_origin()
@jwt_required
def probe():
    user = get_current_user()
    if not user:
        return abort(401)
    if "local" in user["providers"]:
        luser = local_users.get_local_user(user["uuid"])
        if luser["force_pwd_change"]:
            return jsonify({"force_pwd_change": True}), 200
    return jsonify({"force_pwd_change": False}), 200


# This returns nonfresh access_token with reset force_pwd_change user claim
@app.route("/users/me", methods=["PATCH"])
@cross_origin()
@jwt_required
@fresh_jwt_required
def change_password():
    data = request.json
    if not data:
        return abort(400)
    password = data.get("password", None)
    new_password = data.get("new_password", None)
    new_password_confirmation = data.get("new_password_confirmation", None)
    if (
        not password
        or not new_password
        or not new_password_confirmation
        or new_password != new_password_confirmation
    ):
        return abort(400)

    user = get_current_user()
    if not user:
        return abort(401)

    local = local_users.get_local_user(user["uuid"])
    if not local:
        return abort(401)

    if not bcrypt.checkpw(password.encode("utf8"), local["pwd_hash"].encode("utf8")):
        return abort(401)

    pwd_hash = bcrypt.hashpw(new_password.encode("utf8"), bcrypt.gensalt())
    local_users.update_local_user(
        pwd_hash=pwd_hash.decode("utf8"), force_pwd_change=False, user_uuid=user["uuid"]
    )

    userdata = dict(user)
    userdata.update({"force_pwd_change": False, "user_uuid": user["uuid"]})
    return jsonify({"access_token": create_access_token(identity=userdata)}), 200


@app.route("/users/me/tokens", methods=["GET"])
@cross_origin()
@jwt_required
@fresh_jwt_required
def list_api_tokens():
    items = []
    for token in api_tokens.get_tokens_for_user_uuid(get_jwt_identity(), revoked=False):
        items.append(
            {
                "jti": token["jti"],
                "name": token["name"],
                "created": token["created"].isoformat(),
                "revoked": token["revoked"],
            }
        )
    return jsonify({"items": items}), 200


@app.route("/users/me/tokens", methods=["POST"])
@cross_origin()
@jwt_required
@fresh_jwt_required
def create_api_token():
    data = request.json
    if not data:
        return abort(400)
    name = data.get("name", None)
    if not name:
        return abort(400)

    user = get_current_user()
    if not user:
        return abort(401)
    token = create_access_token(identity=user, expires_delta=False)
    jti = decode_token(token)["jti"]
    api_tokens.add_token(user_uuid=user["uuid"], jti=jti, name=name)
    response = {"access_token": token, "name": name, "jti": jti}
    return jsonify(response), 201


@app.route("/users/me/tokens/<jti>", methods=["DELETE"])
@cross_origin()
@jwt_required
@fresh_jwt_required
def revoke_api_token(jti):
    token = api_tokens.get_token(jti)
    if token is None or token["revoked"]:
        return abort(404)
    if get_jwt_identity() != token["user_uuid"]:
        return abort(401)
    api_tokens.revoke_token(jti)
    return "", 204