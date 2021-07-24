import praw
import re
from datetime import datetime
import mysql.connector
#from threading import Thread

#Need to implement Try-Catch once confirmed working

#Praw data types and attributes: https://praw.readthedocs.io/en/latest/code_overview/praw_models.html
#Spacy data types and attributes: https://spacy.io/api
#MySQL python connector resources: https://dev.mysql.com/doc/connector-python/en/
#Python Regular Expressions: https://docs.python.org/3/library/re.html

# make data in class object for simplicity sake

class User():

    def __init__(self, username):
        self.username = username

    def __init__(self, username, age_gender, unix_time):
        self.username = username
        self.agestamp = unix_utc_toString(unix_time)
        self.format_age_gender(age_gender)
        self.initial_save()

    gender = age = agestamp = location = dob = None

    def get_redditor(self):
        return login().redditor(self.username)
    
    def format_age_gender(self, string):
        # string must be in format DDC
        # where D is digit and C is char
        self.age = int(str(string[0]) + str(string[1]))
        if string[2] == "m":
            self.gender = "Male"
        elif string[2] == "f":
            self.gender = "Female"

    def initial_save(self):
        # saves user to sql database when created
        # through init with age_gender stamp
        db = opendb()
        cur = db.cursor()
        sql_exec_userdata(cur, self)
        db.commit()
        db.close()

    def load_data_from_db(self):
        cur = opendb().cursor()
        cur.execute("SELECT gender,age,agestamp FROM userdata WHERE username=%s",self.username)
        val = cur.fetchone()
        if val is not None:
            self.gender = val
        val = cur.fetchone()
        if val is not None:
            self.age = val
        val = cur.fetchone()
        if val is not None:
            self.agestamp = val

    def save_user_to_db(self):
        # IF EXISTS THEN UPDATE INFO
        pass

    def save_comments_to_db(self):
        db = opendb()
        cur = db.cursor()
        redditor = self.get_redditor()
        print("am I being executed?")
        for comment in redditor.comments.new(limit=max):
            sql_exec_commentdata(cur, comment)
        db.commit()
        db.close()

    def save_posts_to_db(self):
        db = opendb()
        cur = db.cursor()
        redditor = self.get_redditor()
        for post in redditor.submissions.new(limit=max):
            sql_exec_postdata(cur, post)
        db.commit()
        db.close()

    def delete_from_db(self):
        pass
        # Going to need to delete posts and comments first then delete
        # the userdata

    def check_for_existing(self, username=None, cid=None, pid=None):
        if username is not None:
            pass
        elif cid is not None:
            pass
        elif pid is not None:
            pass
        else:
            print("Error None type given where username, cid, or pid must not be None")
            return None

        

def initdb():
    pw = input("Admin password:")
    db = mysql.connector.connect(
            host="192.168.1.101",
            user="Admin",
            password=pw,
            auth_plugin='mysql_native_password'
        )
    cur = db.cursor()
    cur.execute("CREATE DATABASE testdata")
    db.commit()
    db.close()

def deletedb():
    pw = input("Admin password:")
    db = mysql.connector.connect(
        host="192.168.1.101",
        user="Admin",
        password=pw,
        auth_plugin='mysql_native_password'
    )
    cur = db.cursor()
    cur.execute("DROP DATABASE testdata")
    db.commit()
    db.close()

def opendb():
    db = mysql.connector.connect(
        host="192.168.1.101",
        user="Ryan",
        password="password",
        database="testdata",
        auth_plugin='mysql_native_password'
    )
    return db

def opendbAdmin():
    pw = input("Admin password:")
    db = mysql.connector.connect(
        host="192.168.1.101",
        user="Admin",
        password=pw,
        database="testdata",
        auth_plugin='mysql_native_password'
    )
    return db


def backupdb():
    #backup sql database to local and remote repo
    pass

def resetdb():
    db = opendbAdmin()
    cur = db.cursor()
    cur.execute("DROP TABLE IF EXISTS usercommentdata")
    cur.execute("DROP TABLE IF EXISTS userpostdata")
    cur.execute("DROP TABLE IF EXISTS userdata")
    cur.execute("CREATE TABLE userdata(username VARCHAR(30) NOT NULL PRIMARY KEY, gender VARCHAR(15), age INT, agestamp DATETIME, location VARCHAR(95), dob DATE)")
    cur.execute("CREATE TABLE usercommentdata(username VARCHAR(30) NOT NULL, cid VARCHAR(15) NOT NULL PRIMARY KEY, comment TEXT, date DATETIME, FOREIGN KEY(username) REFERENCES userdata(username))")
    cur.execute("CREATE TABLE userpostdata(username VARCHAR(30) NOT NULL, pid VARCHAR(15) NOT NULL PRIMARY KEY, title TEXT, selftext TEXT, date DATETIME, FOREIGN KEY(username) REFERENCES userdata(username))")
    db.commit()
    db.close()

def login():
    reddit = praw.Reddit("py-bot-master")
    return reddit

def unix_utc_toString(unix_string):
    return datetime.utcfromtimestamp(unix_string).strftime('%Y-%m-%d %H:%M:%S')

def sql_exec_userdata(cursor, user):
    try:
        sql = ("INSERT INTO userdata "
                "(username, gender, age, agestamp) "
                "VALUES (%s, %s, %s, %s)")
        val = (user.username, user.gender, user.age, user.agestamp)
        #print(user.username, user.gender, user.age, user.agestamp)
        cursor.execute(sql, val)
    except:
        #print("Error inserting userdata\nKey: " + user.username)
        pass

def sql_exec_commentdata(cursor, comment):
    #(username VARCHAR(30) NOT NULL, cid VARCHAR(15) NOT NULL PRIMARY KEY, comment TEXT, date DATETIME, FOREIGN KEY(username) REFERENCES userdata(username))
    try:
        sql = ("INSERT INTO usercommentdata "
                "(username, cid, comment, date) "
                "VALUES (%s, %s, %s, %s)")
        val = (comment.author.name, comment.id, comment.body, unix_utc_toString(comment.created_utc))
        #print(comment.author.name, comment.id, comment.body, unix_utc_toString(comment.created_utc))
        cursor.execute(sql, val)
    except:
        #print("Error inserting commentdata\nKey: " + comment.id)
        pass

def sql_exec_postdata(cursor, post):
    #(username VARCHAR(30) NOT NULL, pid VARCHAR(15) NOT NULL PRIMARY KEY, title TEXT, selftext TEXT, date DATETIME, FOREIGN KEY(username) REFERENCES userdata(username))
    try:
        sql = ("INSERT INTO userpostdata "
                "(username, pid, title, selftext, date) "
                "VALUES (%s, %s, %s, %s, %s)")
        val = (post.author.name, post.id, post.title, post.selftext, unix_utc_toString(post.created_utc))
        #print(post.author.name, post.id, post.title, post.selftext, unix_utc_toString(post.created_utc))
        cursor.execute(sql, val)
    except:
        #print("Error inserting postdata\nKey: " + post.id)
        pass
    

def collect(reddit):
    subreddit = reddit.subreddit("Relationships")
    for submission in subreddit.stream.submissions():
        title = submission.title.lower()
        search = re.search("(i|my|i'm|i am|me) +\(([1-9][0-9][mf])\)", title)
        if search:
            User(submission.author.name, search.group(2), submission.created_utc)

def run():
    collect(login())

def test1_1():
    reddit = login()
    db = opendb()
    cur = db.cursor()
    me = reddit.redditor("DesolateWolf")
    sql_exec_userdata(cur, me.name)
    for comment in me.comments.new(limit=10):
        sql_exec_commentdata(cur, comment)
    db.commit()
    db.close()

def test1_2():
    db = opendb()
    cur = db.cursor()
    cur.execute("SELECT comment FROM usercommentdata WHERE username='DesolateWolf'")
    vals = cur.fetchone()
    while vals is not None:
        print(vals)
        vals = cur.fetchone()
    resetdb()

def test2_1():
    resetdb()
    reddit = login()
    db = opendb()
    cur = db.cursor()
    data = collect(reddit, 100)
    cur.execute("SELECT * FROM userdata")
    vals = cur.fetchall()
    for val in vals:
        print(val)

def test2_0():
    me = User("DesolateWolf")
    redditor = me.get_redditor()
    print(redditor.name)
    print("end")

def test3_0():
    db = opendb()
    cur = db.cursor()
    cur.execute("SELECT * FROM userdata")
    x = cur.fetchall()
    for i in x:
        print(i)
    cur.execute("SELECT * FROM usercommentdata")
    x = cur.fetchall()
    for i in x:
        print(i)


if __name__ == "__main__":
    run()