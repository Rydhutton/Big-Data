import praw
import re
from datetime import datetime
import mysql.connector
from time import sleep
#import threading
from threading import Thread, active_count as active_thread_count

#Need to implement Try-Catch once confirmed working

#Praw data types and attributes: https://praw.readthedocs.io/en/latest/code_overview/praw_models.html
#Spacy data types and attributes: https://spacy.io/api
#MySQL python connector resources: https://dev.mysql.com/doc/connector-python/en/
#Python Regular Expressions: https://docs.python.org/3/library/re.html

# make data in class object for simplicity sake

GLOBAL_IPV4 = "localhost"

# *************** OBJECT CLASSES ***************

class User():

    username: str
    gender = age = agestamp = location = dob = None

    def __init__(self, username, age_gender=None, unix_time=None):
        self.username = username
        if age_gender is not None: 
            self.format_age_gender(age_gender)
            if unix_time is not None: 
                self.agestamp = unix_utc_toString(unix_time)
                self.initial_save()

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

    def save_comments_to_db(self):
        db = opendb()
        cur = db.cursor()
        redditor = self.get_redditor()
        count = 0
        for comment in redditor.comments.new(limit=1000):
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

    def thread_save_to_db(self):
        commentThread = Thread(target=self.save_comments_to_db)
        postThread = Thread(target=self.save_posts_to_db)
        # might remove daemon, need for testing now
        commentThread.daemon = True
        postThread.daemon = True
        commentThread.start()
        postThread.start()
        commentThread.join()
        postThread.join()

    def delete_from_db(self):
        if input("Are you sure? Press Y for yes").lower() == "y":
            dba = opendbAdmin()
            cur = dba.cursor()
            cur.execute("DELETE FROM userpostdata VALUES * WHERE username=%s",(self.username,))
            cur.execute("DELETE FROM usercommentdata VALUES * WHERE username=%s",(self.username,))
            cur.execute("DELETE FROM userdata VALUES * WHERE username=%s",(self.username,))
            dba.commit()
            dba.close()

    def check_for_existing(self, username=None, cid=None, pid=None):
        booleans = []
        db = opendb()
        cur = db.cursor()
        def search(query, target):
            cur.execute(query, (target,))
            d = cur.fetchone()
            if d is not None:
                for i in d:
                    if i == target:
                        return True
            else: return False
        if username is not None: booleans.append(search("SELECT username FROM userdata WHERE username=%s", username))
        if cid is not None: booleans.append(search("SELECT cid FROM usercommentdata WHERE cid=%s", cid))
        if pid is not None: booleans.append(search("SELECT pid FROM userpostdata WHERE pid=%s", pid))
        return booleans


# **************** SQL DATABASE FUNCTIONS *****************

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
    # Resets the database to a blank state, data will be lost
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
    # Use to delete any accounts in the database which have been deleted or suspended from reddit
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

def sql_exec_userdata(cursor, user):
    try:
        sql = ("INSERT INTO userdata "
                "(username, gender, age, agestamp) "
                "VALUES (%s, %s, %s, %s)")
        val = (user.username, user.gender, user.age, user.agestamp)
        cursor.execute(sql, val)
    except: pass

def sql_exec_commentdata(cursor, comment):
    try:
        sql = ("INSERT INTO usercommentdata "
                "(username, cid, comment, date) "
                "VALUES (%s, %s, %s, %s)")
        val = (comment.author.name, comment.id, comment.body, unix_utc_toString(comment.created_utc))
        cursor.execute(sql, val)
    except: pass

def sql_exec_postdata(cursor, post):
    try:
        sql = ("INSERT INTO userpostdata "
                "(username, pid, title, selftext, date) "
                "VALUES (%s, %s, %s, %s, %s)")
        val = (post.author.name, post.id, post.title, post.selftext, unix_utc_toString(post.created_utc))
        cursor.execute(sql, val)
    except: pass


#********************** COLLECTOR FUNCTIONS ***********************

def login():
    reddit = praw.Reddit("py-bot-master")
    return reddit

def unix_utc_toString(unix_string):
    return datetime.utcfromtimestamp(unix_string).strftime('%Y-%m-%d %H:%M:%S')

def create_user(User):
    # Create a method to thread the creation of a new user so that the main thread can keep
    # monitoring the stream
    pass
    
def collect(reddit, limit=None):
    if limit == None:
        subreddit = reddit.subreddit("Relationships")
        for submission in subreddit.stream.submissions():
            title = submission.title.lower()
            search = re.search("(i|my|i'm|i am|me) +\(([1-9][0-9][mf])\)", title)
            if search:
                target = User(submission.author.name, age_gender=search.group(2), unix_time=submission.created_utc)
                target.save_comments_to_db()
                target.save_posts_to_db()
    else:
        subreddit = reddit.subreddit("Relationships")
        count = 0
        for submission in subreddit.stream.submissions():
            title = submission.title.lower()
            search = re.search("(i|my|i'm|i am|me) +\(([1-9][0-9][mf])\)", title)
            if search:
                count += 1
                target = User(submission.author.name, age_gender=search.group(2), unix_time=submission.created_utc)
                print(target.username)
                target.thread_save_to_db()
            if count >= limit:
                break
                
def new_collect(subreddit, limit=None):
    if limit == None:
        subreddit = reddit.subreddit("Relationships")
        for submission in subreddit.stream.submissions():
            title = submission.title.lower()
            search = re.search("(i|my|i'm|i am|me) +\(([1-9][0-9][mf])\)", title) # Need to modify the RE to be () or []
            if search:
                target = User(submission.author.name, age_gender=search.group(2), unix_time=submission.created_utc)
                target.save_comments_to_db()
                target.save_posts_to_db()
    else:
        subreddit = reddit.subreddit("Relationships")
        count = 0
        for submission in subreddit.stream.submissions():
            title = submission.title.lower()
            search = re.search("(i|my|i'm|i am|me) +\(([1-9][0-9][mf])\)", title)
            if search:
                count += 1
                target = User(submission.author.name, age_gender=search.group(2), unix_time=submission.created_utc)
                print(target.username)
                target.thread_save_to_db()
            if count >= limit:
                break
        
def prod_run():
    reddit = login()
    r_relationships = reddit.subreddit("Relationships")
    r_dating = reddit.subreddit("dating")
    r_relationship_advice = reddit.subreddit("relationship_advice")
    #new_collect(subreddit,limit=None)
    r_relationships_thread = Thread(target=new_collect)
    r_dating_thread = Thread(target=new_collect)
    # add others
    r_relationships_thread.daemon = True
    r_dating_thread.daemon = True
    r_dating_thread.start()
    r_dating_thread.join()
    # INCOMPLETE PLEASE FINISH

# TESTS

# TEST 0: Repetitive functions for testing purposes
def test0_print_userdata(cur):
    cur.execute("SELECT * FROM userdata")
    x = cur.fetchall()
    for i in x:
        print(i)

def test0_print_usercommentdata(cur):
    cur.execute("SELECT * FROM usercommentdata")
    x = cur.fetchall()
    for i in x:
        print(i)

def test0_print_userpostdata(cur):
    cur.execute("SELECT * FROM userpostdata")
    x = cur.fetchall()
    for i in x:
        print(i)


# TEST 1: Testing SQL database functionality

def test1_0():
    reddit = login()
    db = opendb()
    cur = db.cursor()
    me = reddit.redditor("DesolateWolf")
    sql_exec_userdata(cur, me.name)
    for comment in me.comments.new(limit=10):
        sql_exec_commentdata(cur, comment)
    db.commit()
    db.close()

def test1_1():
    db = opendb()
    cur = db.cursor()
    cur.execute("SELECT comment FROM usercommentdata WHERE username='DesolateWolf'")
    vals = cur.fetchone()
    while vals is not None:
        print(vals)
        vals = cur.fetchone()
    resetdb()

def test1_2():
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

# TEST 2: Testing User class functionality

def test2_0():
    me = User("DesolateWolf")
    redditor = me.get_redditor()
    print(redditor.name)
    print("end")

def test2_1():
    resetdb()
    reddit = login()
    db = opendb()
    cur = db.cursor()
    collect(reddit, limit=100)
    cur.execute("SELECT * FROM userdata")
    vals = cur.fetchall()
    for val in vals:
        print(val)

def test2_2():
    u1 = User(username="2KareDogs")
    u2 = User(username="ThisUserDoesNotExist")

    val = u1.check_for_existing(username=u1.username)
    print(val)
    val = u1.check_for_existing(username=u1.username, cid="asdas", pid="asdas")
    print(val)
    val = u2.check_for_existing(username=u2.username)
    print(val)

# TEST 3: Testing database cleaning

def test3_0():
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

# TEST 4: Testing threading

def test4_0():
    print(active_thread_count())

def test4_1():
    resetdb()
    prod_run()


# ******************** MAIN ********************
# used to test for now

if __name__ == "__main__":
  pass


# CAN ONLY BE RUN IN PYTHON 3.10+
# cmdline help menu with new search matching
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
