# Step 1: Importing libraries
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from flask import render_template, flash, Markup

from github import Github

import pprint
import os
import sys
import traceback

#List of files to replicate
FILES = [
	'app.py',
	'.flaskenv',
	'Procfile',
	'wakeup.py',
	'.gitattributes',
	'README.md',
	'installation.md',
	'tech_specs.md',
	'app/routes.py',
	'app/__init__.py',
	'app/static/css/style.css',
	'app/static/js/script.js',
	'app/templates/index.html'
]


def create_file(path, user, password, repo):
	with open(path) as f:
		filename = f.read()
	filename = base64.b64encode(bytes(filename, 'utf-8'))
	file = {'path': path, 'message':'add {}'.format(path), 'content': filename.decode("utf-8")}
	add_file = requests.put('https://api.github.com/repos/{}/{}/contents/{}'.format(user, repo, path), auth=(user, password), data=json.dumps(file))


# Step 2: checking if the key variables are defined. They act as keys that need be 
# defined for the OAuth communication between this webapp and Github to work correctly. 
class GithubOAuthVarsNotDefined(Exception):
    '''raise this if the necessary env variables are not defined '''

if os.getenv('GITHUB_CLIENT_ID') == None or \
        os.getenv('GITHUB_CLIENT_SECRET') == None or \
        os.getenv('APP_SECRET_KEY') == None:
    print(os.getenv('GITHUB_CLIENT_ID'))
    print(os.getenv('GITHUB_CLIENT_SECRET'))
    print(os.getenv('APP_SECRET_KEY'))
    raise GithubOAuthVarsNotDefined('''
      Please define environment variables:
         GITHUB_CLIENT_ID
         GITHUB_CLIENT_SECRET
         GITHUB_ORG
         APP_SECRET_KEY
      ''')


# Step 3 : creating the app and setting the keys
app = Flask(__name__)

app.debug = False

app.secret_key = os.environ['APP_SECRET_KEY']
oauth = OAuth(app)

# Step 4: define the service to which delegating the login to (Github)
# OAuth requires certain URLs so that it knows where to send the user to be able
# to enter their account information.
# Babak : change scope to public_repo
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'],
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],
    request_token_params={'scope': 'public_repo'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

# Step 5: getting the token and secret 
@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


# Step 6: Giving values to the related login variables
@app.context_processor
def inject_logged_in():
    return dict(logged_in=('github_token' in session))

##Babak : delete later
#@app.context_processor
#def inject_github_org():
#    return dict(github_org=os.getenv('GITHUB_ORG'))


# Step 7: rendering the webpages. login() and logout(), use our OAuth object to 
# log in and authorize a user by first calling the url for the function authorized() 
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.clear()
    flash('You were logged out!')
    return redirect(url_for('home'))


# Step 8 : resp is a variable that holds the message from Github after the user tries to log in. 
# HEre the code checks for several things and have error-handling so that our web 
# app produces information for our user to act upon.
@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()

    if resp is None:
        session.clear()
        login_error_message = 'Access denied: reason=%s error=%s full=%s' % (
            request.args['error'],
            request.args['error_description'],
            pprint.pformat(request.args)
        )
        flash(login_error_message, 'error')
        return redirect(url_for('home'))
    try:
        session['github_token'] = (resp['access_token'], '')
        session['user_data']=github.get('user').data
        github_userid = session['user_data']['login']
        #org_name = os.getenv('GITHUB_ORG')
    except Exception as e:
        session.clear()
        message = 'Unable to login: ' + str(type(e)) + str(e)
        flash(message,'error')
        return redirect(url_for('home'))
    
    #Babak will delete it!!
    try:
        g = Github(resp['access_token'])
        #org = g.get_organization(org_name)
        named_user = g.get_user(github_userid)
        #isMember = org.has_in_members(named_user)
    except Exception as e:
        message = 'Unable to connect to Github with accessToken: ' + resp['access_token'] + " exception info: " + str(type(e)) + str(e)
        session.clear()
        flash(message,'error')
        return redirect(url_for('home'))
    
    #if not isMember:
    #    session.clear() # Must clear session before adding flash message
    #    message = 'Unable to login: ' + github_userid + ' is not a member of ' + org_name + \
    #      '</p><p><a href="https://github.com/logout" target="_blank">Logout of github as user:  ' + github_userid + \
    #      '</a></p>' 
    #    flash(Markup(message),'error')

    else:
        flash('You were successfully logged in')

    return redirect(url_for('home'))

# Step 9: Here is the part that starts the main job of the app after it has logged in
# and given the appropriate access
@app.route('/page1')
def renderPage1():
    if 'user_data' in session:
        user_data_pprint = pprint.pformat(session['user_data'])
    else:
        user_data_pprint = ''
    return render_template('page1.html', dump_user_data=user_data_pprint)

@app.route('/page2')
def renderPage2():
    return render_template('page2.html')

@app.route('/replicate', methods=['POST'])
def replicate():
	user = session['user_data']['login']
	password = session.get('github_token')
	repo = request.form['repo']

	payload = {'name': repo, 'description': 'this is a self-replication app.', 'auto_init': False}
	login = requests.post('https://api.github.com/user/repos', auth=(user, password), data=json.dumps(payload))

	for file in FILES:
		create_file(file, user, password, repo)

	if login.status_code == 201:
		return jsonify({'success' : 'Repo is replicated', 'user' : user})
	return jsonify({'error' : login.json()['message']})


if __name__ == "__main__":
    # A workaround after facing at=error code=H10 on Heroku. Because the port is dynamically set in Heroku
    port = int(os.environ.get("PORT", 5000))

    app.run(host='0.0.0.0', port=port)



