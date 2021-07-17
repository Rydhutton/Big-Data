import praw
import re
from datetime import datetime
import mysql.connector


def makedb():
    mydb = mysql.connector.connect(
                host="localhost",
                user="Ryan",
                password="Bl3aK",
                database="testdata"
            )
    mycur = mydb.cursor()
    mycur.execute("CREATE DATABASE testdata")
    mydb.database = "testdata"
    mycur.execute("CREATE TABLE userdata (uid INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(30) NOT NULL, gender VARCHAR(15), age INT, agestamp DATETIME, location VARCHAR(100), dob DATE)")
    mycur.execute("CREATE TABLE usercommentdata (uid INT NOT NULL, comment TEXT, date DATETIME)")
    mycur.execute("CREATE TABLE userpostdata (uid INT NOT NULL, post TEXT, date DATETIME)")
    mydb.commit()
    mydb.close()

def opendb():
    db = mysql.connector.connect(
        host="localhost",
        user="Ryan",
        password="Bl3aK",
        database="testdata"
    )
    return db

def login():
    reddit = praw.Reddit("py-bot-master")
    return reddit
    
def collect(reddit, maxcount):
    count = 0
    data = []
    subreddit = reddit.subreddit("Relationships")
    for submission in subreddit.stream.submissions():
        title = submission.title.lower()
        search = re.search("(i|my|i'm|i am|me) +\(([1-9][0-9][a-z])\)", title)
        if search:
            print(submission.author)
            data.append((submission.author,search.group(2),datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),submission))
            print(search.group(2))
            count += 1
        if count >= maxcount:
            break
    return data

def save_userdata(data):
    db = opendb()
    cur = db.cursor()
    # username VARCHAR(30) NOT NULL, uid INT AUTO_INCREMENT PRIMARY KEY, gender VARCHAR(15), age INT, dob DATE, location VARCHAR(100)
    for account in data:
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
        sql_save_userdata(cur, username, gender, age, agestamp)
    db.commit()
    db.close()

def sql_save_userdata(cursor, username = None, gender = None, age = None, agestamp = None):
    sql = ("INSERT INTO userdata "
            "(username, gender, age, agestamp) "
            "VALUES (%s, %s, %s, %s)")
    val = (username, gender, age, agestamp)
    cursor.execute(sql, val)


if __name__ == "__main__":
    accs = collect(login(),10)
    for acc in accs:
        print(acc[0])
        print(acc[1])
        print(acc[2])
        print(acc[3].title)