import json
import os
import uuid
from flask import Flask, request, redirect, make_response
from requests_oauthlib import OAuth2Session

from config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_SCOPE, GITHUB_ACCESS_TOKEN_URL, \
    GITHUB_AUTHORIZE_URL
from lib import get_most_used_libraries

app = Flask(__name__)

# MAKE A PROPER DB
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
db = {}

@app.route("/", methods=['GET'])
def index():
    # TODO: [Graphics] Index
    return 'index'


@app.route("/login", methods=['GET'])
def login():
    session_id = request.cookies.get('session_id')
    if not session_id or session_id not in db:
        github = OAuth2Session(GITHUB_CLIENT_ID, scope=GITHUB_SCOPE)
        authorization_url, state = github.authorization_url(GITHUB_AUTHORIZE_URL)
        return redirect(authorization_url)
    return redirect('/')


# TODO: Change for /callback
@app.route("/oauth", methods=['GET'])
def oauth():
    if 'code' not in request.args:
        # TODO: [Graphics] 404
        return ''
    code = request.args['code']
    github = OAuth2Session(GITHUB_CLIENT_ID, scope=GITHUB_SCOPE)
    r = github.fetch_token(GITHUB_ACCESS_TOKEN_URL, client_secret=GITHUB_CLIENT_SECRET,
                           code=code)
    access_token = r['access_token']

    session_id = str(uuid.uuid4())
    db[session_id] = access_token

    response = make_response(redirect('/'))
    response.set_cookie('session_id', session_id)
    return response


@app.route("/stats", methods=['GET', 'POST'])
def stats():
    pass
    # TODO: [Graphics] Loading spinner
    # Get the cookie from request data
    session_id = request.cookies.get('session_id')
    if session_id not in db:
        response = make_response(redirect('/'))
        response.set_cookie('session_id', '', expires=0)
        return response
    # Get the access_token from database
    access_token = db[session_id]
    github = OAuth2Session(GITHUB_CLIENT_ID, token={'access_token': access_token})
    TOTAL_LIBRARIES = get_most_used_libraries(github)
    return json.dumps(TOTAL_LIBRARIES)


if __name__ == '__main__':
    app.debug = True
    app.run()
