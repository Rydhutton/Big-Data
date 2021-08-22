from collector import *

class User():

    username: str
    gender: str
    age: int
    gender, age, agestamp, location, dob = None

    def __init__(self, username, age_gender=None, unix_time=None):
        self.username = username
        if age_gender: 
            self.format_age_gender(age_gender)
            if unix_time: 
                self.agestamp = unix_utc_toString(unix_time)
                self.initial_save()

    def __bool__(self):
        r = self.get_redditor()
        try:
            _ = r.comment_karma
            return True
        except:return False

    def get_redditor(self):
        return login().redditor(self.username)
    
    def format_age_gender(self, string):
        self.age = int(str(string[0]) + str(string[1]))
        if string[2] == "m":
            self.gender = "Male"
        elif string[2] == "f":
            self.gender = "Female"

    def initial_save(self):
        db = opendb()
        cur = db.cursor()
        sql_exec_userdata(cur, self)
        db.commit()
        db.close()

    def load_data_from_db(self):
        cur = opendb().cursor()
        cur.execute("SELECT gender,age,agestamp FROM userdata WHERE username=%s",self.username)
        val = cur.fetchone()
        if val:
            self.gender = val
        val = cur.fetchone()
        if val:
            self.age = val
        val = cur.fetchone()
        if val:
            self.agestamp = val

    def save_comments_to_db(self):
        db = opendb()
        cur = db.cursor()
        redditor = self.get_redditor()
        miss = 0
        for comment in redditor.comments.new(limit=1000):
            if sql_exec_commentdata(cur, comment) == False:
                miss += 1
                if miss >= 10: break
            else: miss = 0
        db.commit()
        db.close()

    def save_posts_to_db(self):
        db = opendb()
        cur = db.cursor()
        redditor = self.get_redditor()
        miss = 0
        for post in redditor.submissions.new(limit=1000):
            if sql_exec_postdata(cur, post) == False:
                miss += 1
                if miss >= 10: break
            else: miss = 0
        db.commit()
        db.close()

    def thread_save_to_db(self):
        commentThread = Thread(target=self.save_comments_to_db)
        postThread = Thread(target=self.save_posts_to_db)
        commentThread.daemon = True
        postThread.daemon = True
        commentThread.start()
        postThread.start()
        commentThread.join()
        postThread.join()

    def delete_from_db(self, admin_password=None):
        if input("Are you sure? Press Y for yes").lower() == "y":
            dba = opendbAdmin(admin_password=admin_password)
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
            if d:
                for i in d:
                    if i == target:
                        return True
            else: return False
        if username: booleans.append(search("SELECT username FROM userdata WHERE username=%s", username))
        if cid: booleans.append(search("SELECT cid FROM usercommentdata WHERE cid=%s", cid))
        if pid: booleans.append(search("SELECT pid FROM userpostdata WHERE pid=%s", pid))
        if len(booleans) > 1: return booleans
        else: return booleans[0]