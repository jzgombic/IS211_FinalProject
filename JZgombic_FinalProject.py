#!/usr/bin/env python
# -*- coding: utf-8 -*-


from contextlib import closing as cls
from flask import Flask, session, g, flash
from flask import request as req
from flask import redirect as rd
from flask import url_for as furl
from flask import render_template as template
import os
import sqlite3 as sql


DATABASE = 'blog.db'
SECRET_KEY = os.urandom(24)
USERNAME = 'admin'
PASSWORD = 'password'


app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sql.connect(app.config['DATABASE'])


def init_db():
    with cls(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def home():
    cur1 = g.db.execute('SELECT published, title, author, comments from posts ORDER BY published DESC')
    posts = [dict(published=row[0], title=row[1], author=row[2], content=row[3]) for row in cur1.fetchall()]
    return template('home.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if req.method == 'POST':

        if req.form['username'] != app.config['USERNAME']:
            error = 'Invalid username. Please try again.'
            return template('login.html', error=error)

        if req.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password. Please try again.'
            return template('login.html', error=error)

        else:
            session['logged_in'] = True
            flash('Login Successful')
            return rd(furl('dashboard'))

    else:
        return template('login.html', error=error)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    cur1 = g.db.execute('SELECT published, title, author, id, comments from POSTS ORDER BY published DESC')
    posts = [dict(published=row[0], title=row[1], author=row[2], postID=row[3], comments=row[4]) for row in cur1.fetchall()]
    return template('dashboard.html', posts=posts)


@app.route('/post/add', methods=['GET', 'POST'])
def add():

    if req.method == 'GET':
        return template('add.html')

    if req.method == 'POST':

        if not session.get('logged_in'):
            return rd('/login')

        try:
            g.db.execute('INSERT INTO POSTS (published, title, author, comments) VALUES (?,?,?,?)', (req.form['published'].title(), req.form['title'].title(), req.form['author'].title(), req.form['postText'].title()))
            g.db.commit()
            flash('Post was successfully added')
            return rd('/dashboard')

        except:
            flash("Somthing went wrong! Post not added.")
            return rd('/post/add')


@app.route('/post/edit/<post_id>', methods=['GET', 'POST'])
def edit(postID):

    if req.method == 'GET':

        if not session.get('logged_in'):
            return rd('/login')

        cur10 = g.db.execute('SELECT published, title, author, id, comments from posts WHERE id = ?', (postID))
        edit = [dict(published=row[0], title=row[1], author=row[2], postID=row[3], comments=row[4]) for row in cur10.fetchall()]
        return template('edit.html', postID=postID, edit=edit)

    if req.method == 'POST':

        if not session.get('logged_in'):
            return rd('/login')

        try:
            date = req.form['date']
            title = req.form['title']
            author = req.form['author']
            content = req.form['comments']
            query = ('UPDATE POSTS SET published = ?, title = ?, author = ?, comments = ? WHERE id =?')
            g.db.execute(query, (published, title, author, comments, postID))
            g.db.commit()
            return rd('/dashboard')

        except:
            flash("Something went wrong! Post not changed.")
            return rd('/post/edit/<postID>')


@app.route('/post/delete/<post_id>', methods=['GET', 'POST'])
def delete(postID):

    if not session.get('logged_in'):
        return rd('/login')

    else:

        try:
            g.db.execute('DELETE FROM POSTS WHERE id = (?)', (postID))
            g.db.commit()
            flash('Post deleted')
            return rd('/dashboard')

        except:
            flash("Error! Post not deleted.")
            return rd('/dashboard')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return rd('/')



if __name__ == '__main__':
    app.run(DEBUG = True)
