from collector import *

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


if __name__ == "__main__":
    pass