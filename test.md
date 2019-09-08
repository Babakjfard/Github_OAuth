ReplOAuth – A self-replicating app
==================================

Installation Document
=====================

This document explains the steps that are needed to take to create a
working copy of this app on your heroku account.

Step 1: Initial preparation of the development environment
----------------------------------------------------------

You will need to have a git installed on your local computer, a heroku
account as the working server for your own version of the app, also a
working environment in python with the required packages. (Having a copy
of this app means that you already have a working github account). You
can skip each section of this part if you have the required systems
already in place and working.

-   Install local git and connecting with your github account: [this
    link](https://help.github.com/en/articles/set-up-git) explains the
    steps you will need to install git and authenticate it with github,
    therefore you can directly connect your local and remote
    repositories.

-   Sign up at Heroku and install Heroku CLI : Heroku is a platform as a
    service (PaaS) that enables developers to build, run, and operate
    applications entirely in the cloud. You can sign up
    [here](https://signup.heroku.com/) and start using it free.

-   Install Heroku CLI: The Heroku Command Line Interface (CLI) makes it
    easy to create and manage your Heroku apps directly from the
    terminal. It’s an essential part of using Heroku. You can follow
    [these
    instructions](https://devcenter.heroku.com/articles/heroku-cli) to
    install it on your system.

Step 2: Make your app to work
-----------------------------

In this step you will follow the instruction to how to create a local
copy of the app, creating a space for the app on heroku, defining the
required keys and pushing the code into heroku.

### 

### 2.a. Clone from github to local repository: 

Use the following code in your desired place to get a copy off the app
on your computer.

\$ git clone https://github.com/*YOUR-USERNAME*/*YOUR-REPOSITORY*

Or you can follow the instructions
[here](https://help.github.com/en/articles/cloning-a-repository).

### 2.b. Deploying the app on Heroku

[This link](https://devcenter.heroku.com/articles/git) provides a
comprehensive guide about how to deploy your app on heroku using git and
Heroku CLI. But for the simplicity the steps are provided here. Before
starting, make sure to be in the root directory of your application in
the command line, therefore the remote heroku repository will be
automatically set as the repository for your app.

\$ heroku create *app\_name*

\$ git remote -v

\$ git push heroku master

First line above creates the remote empty repository on your heroku. The
second line checks if the remote repository is created. the last line
deploys the app on heroku.

2.b. Register your OAuth app in your Github
-------------------------------------------

An OAuth App uses GitHub as an identity provider to authenticate as the
user who grants access to the app. This means when a user grants an
OAuth App access, they grant permissions to *all* repositories they have
access to in their account, and also to any organizations they belong to
that haven't blocked third-party access. Note that OAuth Apps are
applications that need to be hosted somewhere (you are hosting it on
heroku). With this introduction you follow the [instructions in this
link](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/)
to create an OAuth app on your github that is hosted on your heroku
repository which you created in the previous step.

When registering your app put the URL to your heroku repository in
**Homepage URL**

and remember for **Authorization callback URL** add */login/authorized*
at the end of url for homepage and put it there.

2.c. Set the Config Vars in heroku
----------------------------------

Github creates a *Client\_Id* and a *Client\_Secret* for your app, that
you can find them in your app’s page at Github. The *client\_id* is a
public identifier for apps. Even though it’s public, it’s best that it
isn’t guessable by third parties, so many implementations use something
like a 32-character hex string. It must also be unique across all
clients that the authorization server handles. If the client ID is
guessable, it makes it slightly easier to craft phishing attacks against
arbitrary applications. the *client\_secret* is a mechanism of
authorizing a client, the software requesting an access token. You might
think of it as a secret passphrase that proves to the authentication
server that the client app is authorized to make a request on behalf of
the user.

Then you open your heroku, open your app, click the *settings* tab on
far right top, and then push the *Reveal Config Vars* button. Then set
the variables and the values for your app as in the following figure.

![A screenshot of a cell phone Description automatically
generated](media/image1.png){width="5.615437445319335in"
height="2.9900984251968503in"}

Use the same name for the variables as in the figure. The values for
GITHUB\_CLIENT\_ID and GITHUB\_CLIENT\_SECRET are what you get from your
git hub account. For creating the APP\_SECRET\_KEY you can run the short
code random\_string.py provided in the root directory of your app to
create a random string of the size you want, then copy and paste it as
the value for this variable.

All done! Now you can trigger your app by typing
*app\_name*.herokuapp.com at your browser.
