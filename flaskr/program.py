from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

### pyBlink
import RPi.GPIO as GPIO
import time

bp = Blueprint('program', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('program/index.html', posts=posts)

@bp.route('/create', methods=(['GET', 'POST']))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('program.index'))

    return render_template('program/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=(['GET', 'POST']))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('program.index'))

    return render_template('program/update.html', post=post)

@bp.route('/<int:id>/run', methods=(['GET']))
@login_required
def run(id):
    post = get_post(id)
    
    print('hello')
    print(post['title'])
    print(post['body'])
    
    run = True
    
    ### pyBlink
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    LED = int(post['title'])
    delay = float(post['body'])
    ledState = False
    GPIO.setup(LED, GPIO.OUT)

    while run:
        GPIO.output(LED, True)
        time.sleep(delay)
        GPIO.output(LED, False)
        time.sleep(delay)
        GPIO.output(LED, True)
        time.sleep(delay)
        GPIO.output(LED, False)
        time.sleep(delay)
        GPIO.output(LED, True)
        time.sleep(delay)
        GPIO.output(LED, False)
        time.sleep(delay)
        run = False
        
    
    return redirect(url_for('program.index')) 



@bp.route('/<int:id>/delete', methods=(['POST']))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('program.index'))