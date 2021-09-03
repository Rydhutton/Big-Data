import mysql.connector
from collector import unix_utc_toString

SQL_SERVER_IPV4 = "localhost"

# **************** SQL DATABASE FUNCTIONS *****************

def initdb():
    pw = input("Admin password:")
    db = mysql.connector.connect(
            host=SQL_SERVER_IPV4,
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
        host=SQL_SERVER_IPV4,
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
        host=SQL_SERVER_IPV4,
        user="Ryan",
        password="password",
        database="testdata",
        auth_plugin='mysql_native_password'
    )
    return db

def opendbAdmin(admin_password=None):
    # opens the SQL server as an administrator
    if admin_password:
        db = mysql.connector.connect(
        host=SQL_SERVER_IPV4,
        user="Admin",
        password=admin_password,
        database="testdata",
        auth_plugin='mysql_native_password'
        )
    else:
        pw = input("Admin password:")
        db = mysql.connector.connect(
            host=SQL_SERVER_IPV4,
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

def importusers():
    db = opendb()
    cur = db.cursor()
    cur.execute("SELECT * FROM userdata")
    dump = cur.fetchall()
    return dump

def sql_exec_userdata(cursor, user):
    try:
        sql = ("INSERT INTO userdata "
                "(username, gender, age, agestamp) "
                "VALUES (%s, %s, %s, %s)")
        val = (user.username, user.gender, user.age, user.agestamp)
        cursor.execute(sql, val)
        return True
    except: return False

def sql_exec_commentdata(cursor, comment):
    try:
        sql = ("INSERT INTO usercommentdata "
                "(username, cid, comment, date) "
                "VALUES (%s, %s, %s, %s)")
        val = (comment.author.name, comment.id, comment.body, unix_utc_toString(comment.created_utc))
        cursor.execute(sql, val)
        return True
    except: return False

def sql_exec_postdata(cursor, post):
    try:
        sql = ("INSERT INTO userpostdata "
                "(username, pid, title, selftext, date) "
                "VALUES (%s, %s, %s, %s, %s)")
        val = (post.author.name, post.id, post.title, post.selftext, unix_utc_toString(post.created_utc))
        cursor.execute(sql, val)
        return True
    except: return False