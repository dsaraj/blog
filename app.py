"""import Flask and SQlite packages"""
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect 
from werkzeug.exceptions import abort

"""
function opens connection to database.db file. Sets row_factory attribute to sqlite3.Row to gain access to name based access to columns
Database connection will return rows that behave like regular Python dictionaries.
Conn.close() closes database connection and returns results. 
"""
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn #returns conn connection object to access database

"""
get_post(post_id) determines what blog plost to return
use get_db_connection() function to open db connection and execute SQL query to 
get blost post associated with give post_id value.
fetchone() method used to get result and store it in post variable and close connection.
If post variable has None value the abort() function will respond with 404 error code.
"""
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vgy7bhu8VGY&BHU*'

"""
Open database connection using get_db_connection() function.
posts function executes SQL query to select all entries from 'posts' table.
fetchall() method fetches all rows of query result
"""
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

"""
new function adds variable <int:post_id> to specify part after (/) is a positive integer
Flask recognizes this and passes its value to post_id of post() view function
get_post() function gets blog post associated with specified ID and stores result in post variable,
which is passed to post.html template.
"""
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

