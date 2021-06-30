import os

from flask import Flask, url_for, request, render_template, json, redirect, make_response, session, abort
from werkzeug.utils import secure_filename
from data import db_session
from data.news import News
from forms.news import NewsForm
from forms.user import LoginForm, RegisterForm, EditForm
from data.users import User
from data.friends import Friends
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.friend import FriendAddForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config["IMAGE_UPLOADS"] = 'static/uploaded_images'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 3 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)


def allowed_image(filename):  # Проверка разрешения файла

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):  # Проверка размера файла
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    avatar = 'default'
    if current_user.is_authenticated:
        avatar = current_user.avatar_id
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    return render_template('index.html', title='Домашняя страница',
                           news=news, avatar=avatar, user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/odd_even')
def odd_even():
    user = User()
    db_sess = db_session.create_session()
    db_sess.commit()

    for user in db_sess.query(User).all():
        print(user)
    return render_template('odd_even.html', number=3)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/news')
def news():
    with open("news.json", "rt", encoding="utf8") as f:
        news_list = json.loads(f.read())
    print(news_list)
    return render_template('news.html', news=news_list)


@app.route('/loop')
def loop():
    return render_template('loop.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            username=form.username.data,
            surname=form.surname.data,
            city=form.city.data,
            avatar_id='NONE.jpg'
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/profile")
def profile():
    if not current_user.is_authenticated:
        return redirect('/login')
    return redirect(f'/profile/{current_user.username}')


@app.route('/profile/<string:username>', methods=['GET', 'POST'])
def profile_user(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()
    if user:

        if current_user.is_authenticated:
            news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != True))
        else:
            news = db_sess.query(News).filter(News.is_private != True)


        return render_template('profile.html', title='Профиль',
                               news=news, user=user)
    else:
        abort(404)


@login_required
@app.route('/edit_avatar/<string:username>', methods=['GET', 'POST'])
def edit_avatar(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()

    if user == current_user:  # не забыть выводить ошибку пользователю
        if request.method == "POST":
            if request.files:
                if "filesize" in request.cookies:
                    if not allowed_image_filesize(request.cookies["filesize"]):
                        print("Filesize exceeded maximum limit")
                        return redirect(request.url)

                    image = request.files["image"]
                    if image.filename == "":
                        print("No filename")
                        return redirect(request.url)

                    if allowed_image(image.filename):
                        filename = secure_filename(image.filename)

                        image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))

                        user.avatar_id = filename
                        db_sess.commit()

                        print("Image saved")

                        return redirect(request.url)

                    else:
                        print("That file extension is not allowed")
                        return redirect(request.url)
    else:
        return redirect(f'/profile/{username}')

    return render_template('edit.html', user=user)


@login_required
@app.route('/edit_info/<string:username>', methods=['GET', 'POST'])
def edit_info(username):
    db_sess = db_session.create_session()
    user_ = db_sess.query(User).filter(User.username == username).first()
    form = EditForm()

    if user_ == current_user:
        if request.method == "GET":
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.username == username
                                              ).first()
            if user:
                form.name.data = user.name
                form.surname.data = user.surname
                form.about.data = user.about
                form.city.data = user.city

            else:
                abort(404)

        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(
                                              User.username == current_user.username
                                              ).first()
            if user:
                user.name = form.name.data
                user.surname = form.surname.data
                user.city = form.city.data
                user.about = form.about.data
                db_sess.commit()
                return redirect(f'/profile/{username}')
            else:
                abort(404)


    else:
        return redirect(f'/profile/{username}')

    return render_template('edit_info.html', form=form)


@login_required
@app.route('/friend_add', methods=['GET', 'POST'])
def friend_add():
    if not current_user.is_authenticated:
        return redirect('/login')

    db_sess = db_session.create_session()
    form = FriendAddForm()
    if form.validate_on_submit():
        username = form.username.data
        user = db_sess.query(User).filter(User.username == username).first()

        if not user:
            return render_template('friend_add.html', message='Такого пользователя не существует', form=form)

        if user == current_user:
            return render_template('friend_add.html', message='Неверный никнейм', form=form)

        if db_sess.query(Friends).filter(Friends.friend_two == user.id).first():
            return render_template('friend_add.html', message='Вы уже отправляли заявку пользователю', form=form)

        friend = Friends(
            friend_one=current_user.id,
            friend_two=user.id,
            status=1
        )

        db_sess.add(friend)
        db_sess.commit()

        return render_template('friend_add.html', message='Запрос добавлен', form=form)

    return render_template('friend_add.html', form=form)


@login_required
@app.route('/friend_accept', methods=['GET', 'POST'])
def friend_accept():
    if not current_user.is_authenticated:
        return redirect('/login')

    db_sess = db_session.create_session()
    friends = db_sess.query(Friends).filter((Friends.friend_two == current_user.id) & (Friends.status == 1)).all()
    users = []

    for i in friends:
        if db_sess.query(Friends).filter((Friends.friend_one == current_user.id) & (Friends.status != 0)).first():
            continue
        users.append(db_sess.query(User).filter(User.id == i.friend_one).first())

    return render_template('friend_accept.html', users=users, sess=db_sess)


@login_required
@app.route('/friend_accepted/<int:id>', methods=['GET', 'POST'])
def friend_accepted(id):
    db_sess = db_session.create_session()

    friend = Friends(
        friend_one=current_user.id,
        friend_two=id,
        status=1
    )

    db_sess.add(friend)
    db_sess.commit()
    return redirect('/friend_accept')


@login_required
@app.route('/friend_rejected/<int:id>', methods=['GET', 'POST'])
def friend_rejected(id):
    db_sess = db_session.create_session()

    friend = Friends(
        friend_one=current_user.id,
        friend_two=id,
        status=-1
    )

    db_sess.add(friend)
    db_sess.commit()
    return redirect('/friend_accept')


@login_required
@app.route('/friends', methods=['GET', 'POST'])
def friends():
    if not current_user.is_authenticated:
        return redirect('/login')

    db_sess = db_session.create_session()
    friends = db_sess.query(Friends).filter((Friends.friend_two == current_user.id) & (Friends.status == 1)).all()
    users = []

    for i in friends:
        if db_sess.query(Friends).filter((Friends.friend_one == current_user.id) & (Friends.status != 1)).first():
            continue
        users.append(db_sess.query(User).filter(User.id == i.friend_one).first())

    return render_template('friends.html', users=users, sess=db_sess)

@login_required
@app.route('/friends', methods=['GET', 'POST'])
def friends():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == current_user.username).first()
    if not current_user.is_authenticated:
        return redirect('/login')
    return render_template('friends.html', user=user)



if __name__ == '__main__':
    main()