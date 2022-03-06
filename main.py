# importing flask module
import sqlite3
import os
from flask import Flask, render_template, request, url_for, flash, redirect, g
from flask_login import current_user, login_required, login_user, logout_user
from flask_login import LoginManager
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from user_login import UserLogin
from fdb import FlDB


def connect_db():
    conn = sqlite3.connect('post_flack.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = connect_db()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


# initializing a variable of Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(20).hex()
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FlDB(db)


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next'))
    if request.method == "POST":
        user = dbase.get_user_by_email(request.form['email'])
        if user:
            if user and check_password_hash(user['psw'], request.form['password']):
                userlogin = UserLogin().create(user)
                login_user(userlogin)
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash("Bad value password", "error")
        elif request.form['rm']:
            user = dbase.add_user(request.form['email'], generate_password_hash(request.form['password']))
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('index'))
        else:
            flash("Bad value e-mail or password", "error")

    return render_template("login.html", title="Авторизация")


# decorating index function with the app.route
@app.route('/')
def index():
    conn = connect_db()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', title=title, post=post)


@app.route('/<int:post_id>')
@login_required
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = connect_db()
            conn.execute('INSERT INTO posts (title, content, owner) VALUES (?, ?, ?)',
                         (title, content, int(current_user.get_id())))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = connect_db()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    conn = connect_db()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        #session.pop('_flashes', None)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash_pass = generate_password_hash(request.form['psw'])
            conn = connect_db()
            conn.execute('INSERT INTO users (name, email, psw) VALUES (?, ?, ?)',
                         (request.form['name'], request.form['email'], hash_pass))
            conn.commit()
            conn.close()
            res = True
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", title="Регистрация")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()
