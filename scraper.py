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

    age = gender = location = dob = None

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
        else:
            self.gender = "Unknown"
            print("Error")

    def initial_save(self):
        pass
        # save to userdata db
        # then save all posts to db
        # then save all comments to db
        # no checking needed as first creation

    def save_user_to_db(self):
        # IF EXISTS THEN UPDATE INFO
        pass

    def save_comments_to_db(self):
        # IF EXISTS DONT SAVE
        pass

    def save_posts_to_db(self):
        # IF EXISTS DONT SAVE
        pass

    def delete_from_db(self):
        pass
        # Going to need to delete posts and comments first then delete
        # the userdata
        


def initdb():
    db = mysql.connector.connect(
            host="localhost",
            user="Ryan",
            password="Bl3aK",
        )
    cur = db.cursor()
    cur.execute("CREATE DATABASE testdata")
    db.commit()
    db.close()

def deletedb():
    db = mysql.connector.connect(
        host="localhost",
        user="Ryan",
        password="Bl3aK",
    )
    cur = db.cursor()
    cur.execute("DROP DATABASE testdata")
    db.commit()
    db.close()

def opendb():
    db = mysql.connector.connect(
        host="localhost",
        user="Ryan",
        password="Bl3aK",
        database="testdata"
    )
    return db

def backupdb():
    #backup sql database to local and remote repo
    pass

def resetdb():
    db = opendb()
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
    
def collect(reddit, maxcount):
    # TO DO: Implement threading to save to DB whenever a new unique user is found
    count = 0
    data = []
    subreddit = reddit.subreddit("Relationships")
    for submission in subreddit.stream.submissions():
        title = submission.title.lower()
        search = re.search("(i|my|i'm|i am|me) +\(([1-9][0-9][a-z])\)", title)
        if search:
            #print(submission.author)
            data.append((submission.author,search.group(2),unix_utc_toString(submission.created_utc),submission))
            #print(search.group(2))
            count += 1
        if count >= maxcount:
            break
    return data

def sql_exec_userdata(cursor, username, gender = None, age = None, agestamp = None):
    sql = ("INSERT INTO userdata "
            "(username, gender, age, agestamp) "
            "VALUES (%s, %s, %s, %s)")
    val = (username, gender, age, agestamp)
    cursor.execute(sql, val)

def sql_exec_commentdata(cursor, comment):
    # first time an account is added to the db it should scan through and add all
    # comments and posts without doing a duplicate checkup
    # then afterwards do a query for comment id before updating to avoid dupes
    #(username VARCHAR(30) NOT NULL FOREIGN KEY, cid INT NOT NULL, comment TEXT, date DATETIME)
    sql = ("INSERT INTO usercommentdata "
            "(username, cid, comment, date) "
            "VALUES (%s, %s, %s, %s)")
    val = (comment.author.name, comment.id, comment.body, unix_utc_toString(comment.created_utc))
    cursor.execute(sql, val)

def sql_exec_postdata(cursor, post):
    #(username VARCHAR(30) NOT NULL FOREIGN KEY, pid INT NOT NULL, title TEXT, selftext TEXT, date DATETIME)
    sql = ("INSERT INTO userpostdata "
            "(username, pid, title, selfttext, date) "
            "VALUES (%s, %s, %s, %s, %s)")
    val = (post.author.name, post.id, post.title, post.selftext, unix_utc_toString(post.created_utc))
    cursor.execute(sql, val)






def save_userdata(data):
    # username VARCHAR(30) NOT NULL, uid INT AUTO_INCREMENT PRIMARY KEY, gender VARCHAR(15), age INT, dob DATE, location VARCHAR(100)
    db = opendb()
    cur = db.cursor()

    def format_to_sql(account):
        redditor = account[0]
        username = redditor.name
        age = str(account[1][0]) + str(account[1][1])
        gender = "Unknown"
        if account[1][2] == "m":
            gender = "Male"
        elif account[1][2] == "f":
            gender = "Female"
        else:
            print("Error")
        agestamp = account[2]
        sql_exec_userdata(cur, username, gender, age, agestamp)

    if type(data) is list:
        for account in data:
            format_to_sql(account)
    elif type(data) is tuple:
        format_to_sql(data)
    else:
        print("error: unknown data type" + type(data))

    db.commit()
    db.close()












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
    reddit = login()
    db = opendb()
    cur = db.cursor()
    data = collect(reddit, 10)
    save_userdata(data)
    for user in data:
        name = user[0].name

def test2_0():
    me = User("DesolateWolf")
    redditor = me.get_redditor()
    print(redditor.name)
    print("end")

if __name__ == "__main__":
    test2_0()