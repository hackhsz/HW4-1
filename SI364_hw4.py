## SI 364 - Fall 2017
## HW 4

## Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
import pdb

#Tweet.query.all()

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecure'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhos\
t/hushizhhw4"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up Flask debug stuff
manager = Manager(app)
db = SQLAlchemy(app) # For database use

## Set up Shell context so it's easy to use the shell to debug
def make_shell_context():
    return dict(app=app, db=db,User=User, Tweet=Tweet) ## TODO SI364: Add your models to this shell context function so you can use them in the shell
    # TODO SI364: Submit a screenshot of yourself using the shell to make a query for all the Tweets in the database.
    # Filling this in will make that easier!




# Add function use to manager
manager.add_command("shell", Shell(make_context=make_shell_context))


#########
######### Everything above this line is important/useful setup, not problem-solving.
#########

##### Set up Models #####

## TODO SI364: Set up the following Model classes, with the respective fields (data types).

## The following relationships should exist between them:
# Tweet:User - Many:One
# Tweet:Hashtag - Many:Many

collections = db.Table('collections',db.Column('tweets_id',db.Integer,db.ForeignKey('tweet.id')),db.Column('hashtags_id',db.Integer,db.ForeignKey('hashtag.id')))



class User(db.Model):
    __tablename__ ="user"
    id = db.Column(db.Integer,primary_key=True)
    twitter_username= db.Column(db.String(64),unique=True)
    tweets = db.relationship('Tweet',backref='User')

    def __repr__(self):
        return "This user is {}".format(self.id)

class Hashtag(db.Model):
    __tablename__ = "hashtag"
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.String(1000),unique=True)
#    tweets = db.relationship('Tweet',backref='Hashtag')
    #why do we need these two lines? 

    def __repr__(self):
        return "This hashtag is {}".format(self.id)

class Tweet(db.Model):
    __tablename__ = "tweet"
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.String(285))
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    hashtag = db.relationship('Hashtag',secondary=collections,backref=db.backref('tweet',lazy='dynamic'),lazy='dynamic')
#    hashtag_id = db.Column(db.Integer,db.ForeignKey("hashtag.id"))


    def __repr__(self):
        return "{} by User id{}".format(self.text,self.user_id)

# - Tweet
## -- id (Primary Key)
## -- text (String, up to 285 chars)
## -- user_id (Integer, ID of user posted)

# - User
## -- id (Primary Key)
## -- twitter_username (String, up to 64 chars) (Unique=True)

# - Hashtag
## -- id (Primary Key)
## -- text (Unique=True)

# Association Table: Tweet_Hashtag
# -- tweet_id
# -- hashtag_id

## NOTE: You'll have to set up database relationship code in either the Tweet table or the Hashtag table so that the association table for that many-many relationship will work properly!


##### Set up Forms #####

# TODO SI364: Fill in the rest of this Form class so that someone running this web app will be able to fill in information about tweets they wish existed to save in the database:

## -- tweet text
## -- the twitter username who should post it
## -- a list of comma-separated hashtags it should have

class TweetForm(FlaskForm):
    text = StringField("What are your text for this tweet?",validators=[Required()])
    username = StringField("What is your twitter user name?",validators=[Required()])
    #hashtag = StringField("What is your  user name?",validators=[Required()])
    hashtags = StringField("What are the hashtags?", validators=[Required()])
    submit = SubmitField('Submit')


##### Helper functions

### For database additions / get_or_create functions

## TODO SI364: Write get_or_create functions for each model -- Tweets, Hashtags, and Users.
## -- Tweets should be identified by their text and user id,(e.g. if there's already a tweet with that text, by that user, then return it; otherwise, create it)
## -- Users should be identified by their username (e.g. if there's already a user with that username, return it, otherwise; create it)

# identifying filter by two columns 



## -- Hashtags should be identified by their text (e.g. if there's already a hashtag with that text, return it; otherwise, create it)

## HINT: Your get_or_create_tweet function should invoke your get_or_create_user function AND your get_or_create_hashtag function. You'll have seen an example similar to this in class!

## NOTE: If you choose to organize your code differently so it has the same effect of not encounting duplicates / identity errors, that is OK. But writing separate functions that may invoke one another is our primary suggestion.


def get_or_create_user(db_session,username):
    user = db_session.query(User).filter_by(twitter_username=username).first()
    if user:
        return user
    else:
        user= User(twitter_username=username)
        db_session.add(user)
        db_session.commit()
#        pdb.set_trace()
 #       print(user.id)
        return user

def get_or_create_hashtag(db_session,htext):
    hashtag = db_session.query(Hashtag).filter_by(text=htext).first()
    if hashtag:
#        print("Hash tag(Found) ",hashtag.text)
        return hashtag
    else:
        hashtag = Hashtag(text=htext)
        
        
        db_session.add(hashtag)
        db_session.commit()
 #       print("Hash tag(Created) ",hashtag.text)
        return hashtag

def get_or_create_tweets(db_session,tweet_text,tweet_user,list_hashtags=[]):
    user = get_or_create_user(db_session,tweet_user)
    
    tweet = db_session.query(Tweet).filter_by(text=tweet_text,user_id=user.id).first()
    if tweet:
        return tweet
    else:
        user = get_or_create_user(db_session,tweet_user)
        tweet = Tweet(text=tweet_text,user_id=user.id)
        for hash_tag in list_hashtags:
            hash_tag = get_or_create_hashtag(db_session,hash_tag)
  #          print(hash_tag.text)
            tweet.hashtag.append(hash_tag)
#        pdb.set_trace()
 #       print(tweet.hashtag)
        db_session.add(tweet)
        db_session.commit()
        return tweet


##### Set up Controllers (view functions) #####

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

## Main route

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TweetForm()
    tweets = Tweet.query.all()
    num_tweets = len(tweets)
    if form.validate_on_submit():
        user = get_or_create_user(db.session,form.username.data)
        if db.session.query(Tweet).filter_by(text =form.text.data,user_id=user.id).first():
            flash("You have already have this tweet with this user")
        newlist=[]
        for item in list(form.hashtags.data.split(",")):
            newlist.append(item.strip("#"))
        print(newlist)
        get_or_create_tweets(db.session,form.text.data,form.username.data,newlist)
        return redirect(url_for('see_all_tweets'))
    return render_template('index.html',form=form,num_tweets = num_tweets)

        # how to filter twice

    ## TODO SI364: Fill in the index route as described.
    # A template index.html has been created and provided to render what this route needs to show -- YOU just need to fill in this view function so it will work.
    ## HINT: Check out the index.html template to make sure you're sending it the data it needs.


    # The index route should:
    # - Show the Tweet form.
    # - If you enter a tweet with identical text and username to an existing tweet, it should redirect you to the list of all the tweets and a message that you've already saved a tweet like that.

    ## ^ HINT: Invoke your get_or_create_tweet function
    ## ^ HINT: Check out the get_flashed_messages setup in the songs app you saw in class

    # This  main page should ALSO show links to pages in the app (see routes below) that:
    # -- allow you to see all of the tweets posted
    # -- see all of the twitter users you've saved tweets for, along with how many tweets they have in your database


@app.route('/all_tweets')
def see_all_tweets():
    all_tweets=[]
    tweets = Tweet.query.all()
#    pdb.set_trace()
    print(len(tweets))
    for tweet in tweets:
        user = User.query.filter_by(id=tweet.user_id).first()
        #hashtag = Hashtag.query.filter_by(id=tweet.hashtag_id).first()
        all_tweets.append((tweet.text,user.twitter_username))
    return render_template('all_tweets.html',all_tweets=all_tweets)

    # TODO SI364: Fill in this view function so that it can successfully render the template all_tweets.html, which is provided.
    ## HINT: Check out the all_songs and all_artists routes in the songs app you saw in class.


@app.route('/all_users')
def see_all_users():
    
    usernames = [(a.twitter_username,len(Tweet.query.filter_by(user_id=a.id).all())) for a in User.query.all()]
    return render_template('all_users.html',usernames=usernames)

    # TODO SI364: Fill in this view function so it can successfully render the template all_users.html, which is provided. (See instructions for more detail.)
    ## HINT: Check out the all_songs and all_artists routes in the songs app you saw in class.


if __name__ == '__main__':
    db.create_all()
    manager.run() # Run with this: python main_app.py runserver
    # Also provides more tools for debugging
