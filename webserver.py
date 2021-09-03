from flask import Flask, render_template, redirect, request, abort
from flask.helpers import url_for
from db import opendb

app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template('homepage.html')

@app.route("/404")
def notfound():
    return render_template('404.html')

@app.route("/<username>")
def search_username(username):
    db = opendb()
    cur = db.cursor()
    cur.execute("SELECT username FROM userdata WHERE username=%s",(username,))
    if cur.fetchone() is None:
        return redirect(url_for('notfound'))
    cur.execute("SELECT * FROM userdata WHERE username=%s",(username,))
    udata = cur.fetchall()
    cur.execute("SELECT * FROM userpostdata WHERE username=%s",(username,))
    pdata = cur.fetchall()
    cur.execute("SELECT * FROM usercommentdata WHERE username=%s",(username,))
    cdata = cur.fetchall()
    return render_template('user.html', username, userinfo = udata, userposts = pdata, usercomments = cdata)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")
# bokeh library?

