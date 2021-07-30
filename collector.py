import praw
import re
from datetime import datetime
import mysql.connector
from time import sleep
#from threading import Thread

#Need to implement Try-Catch once confirmed working

#Praw data types and attributes: https://praw.readthedocs.io/en/latest/code_overview/praw_models.html
#Spacy data types and attributes: https://spacy.io/api
#MySQL python connector resources: https://dev.mysql.com/doc/connector-python/en/
#Python Regular Expressions: https://docs.python.org/3/library/re.html

# make data in class object for simplicity sake

GLOBAL_IPV4 = "192.168.1.101"

class User():

    def __init__(self, username):
        self.username = username

    def __init__(self, username, age_gender=None, unix_time=None):
        self.username = username
        if age_gender is not None: 
            self.format_age_gender(age_gender)
            if unix_time is not None: 
                self.agestamp = unix_utc_toString(unix_time)
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
        count = 0
        for comment in redditor.comments.new(limit=1000):
            print(type(comment))
            print(count)
            count += 1
            sql_exec_commentdata(cur, comment)
        db.commit()
        db.close()

    def save_posts_to_db(self):
        db = opendb()
        cur = db.cursor()
        redditor = self.get_redditor()
        for post in redditor.submissions.new(limit=1000):
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

def setAdminPassword(pwd):
    ADMIN_PASSWORD = pwd

def initdb():
    pw = input("Admin password:")
    db = mysql.connector.connect(
            host=GLOBAL_IPV4,
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
        host=GLOBAL_IPV4,
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
        host=GLOBAL_IPV4,
        user="Ryan",
        password="password",
        database="testdata",
        auth_plugin='mysql_native_password'
    )
    return db

def opendbAdmin(admin_password=None):
    if admin_password is None:
        pw = input("Admin password:")
        db = mysql.connector.connect(
            host=GLOBAL_IPV4,
            user="Admin",
            password=pw,
            database="testdata",
            auth_plugin='mysql_native_password'
        )
    else:
        db = mysql.connector.connect(
        host=GLOBAL_IPV4,
        user="Admin",
        password=admin_password,
        database="testdata",
        auth_plugin='mysql_native_password'
        )
    return db


def backupdb():
    #backup sql database to local and remote repo
    pass

def resetdb():
    # Remakes the database, data will be lost
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

def cleandb(Redditor, admin_password=None):
    # Use to delete any accounts in the database which have been deleted
    try:
        _ = Redditor.comment_karma
        return False
    except:
        print(Redditor.name)
        if admin_password is None: db = opendbAdmin()
        else: db = opendbAdmin(admin_password)
        cur = db.cursor()
        sql = """DELETE FROM userdata WHERE username=%s"""
        val = Redditor.name
        cur.execute(sql, (val,))
        db.commit()
        db.close()
        return True

def login():
    reddit = praw.Reddit("py-bot-master")
    return reddit

def unix_utc_toString(unix_string):
    return datetime.utcfromtimestamp(unix_string).strftime('%Y-%m-%d %H:%M:%S')

def sql_exec_userdata(cursor, user):
    #(username VARCHAR(30) NOT NULL PRIMARY KEY, gender VARCHAR(15), age INT, agestamp DATETIME, location VARCHAR(95), dob DATE)
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
    #(username VARCHAR(30) NOT NULL, cid VARCHAR(15) NOT NULL PRIMARY KEY, comment TEXT, date DATETIME)
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
    #(username VARCHAR(30) NOT NULL, pid VARCHAR(15) NOT NULL PRIMARY KEY, title TEXT, selftext TEXT, date DATETIME)
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
            target = User(submission.author.name)#, search.group(2), submission.created_utc)
            target.save_comments_to_db()
            target.save_posts_to_db()


# CAN ONLY BE RUN IN PYTHON 3.10+
'''
HELP_MENU = {
    "collect: collects incoming stream of users and stores them into userdata",
    "help:    brings up the current help menu"
}

def cmdline():
    def run_command(command: str):
        match command.split:
            case ["collect"]:
                print("collecting... press ctrl + c to exit.")
                collect(login())
            case ["help" | "?"]:
                for line in HELP_MENU:
                    print(line)
            case ["init" | "initialize | makedb", *rest]:
                if "-f" or "-force" in rest:
                    resetdb()
                    initdb()
                else:
                    initdb()
            case ["reset" | "resetdb"]:
                resetdb()
            case _:
                print(f"unknown command: {command!r}.")
    
    while(True):
        cmd = input(">")
        run_command(cmd)
'''

# TESTS

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

def test4_0():
    pw = input("Admin password: ")
    db = opendb()
    cur = db.cursor()
    cur.execute("SELECT * FROM userdata")
    dump = cur.fetchall()
    accounts = []
    for line in dump:
        redditor = User(username=line[0])
        redditor.gender = line[1]
        redditor.age = line[2]
        redditor.agestamp = line[3]
        accounts.append(redditor)
    for acc in accounts:
        #sleep(1)
        Redditor = acc.get_redditor()
        if cleandb(Redditor, admin_password=pw): pass
        else:
            print(acc.username + " is a " + str(acc.age) + " " + acc.gender)
            if Redditor.comment_karma is not None: print("they have " + str(Redditor.comment_karma) + " karma")

def scp_fix():
    db = opendb()
    cur = db.cursor()
    

# NEED TO COMPLETE ABOVE FUNCTION SO THAT IT PARSES CURRENT DATA
# AND INSERTS ALL COMMENTS/POSTS FOR CURRENT USERS AND THEN
# MODIFY COLLECT FUNCTION TO DO THIS ALL THE TIME
# ADD IN THREADING?


if __name__ == "__main__":
    #reddit = login()
    #collect(reddit)
    #cmdline()
    #run()