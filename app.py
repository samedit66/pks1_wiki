from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    abort,
    flash,
)
import os
from article import Article
from database import Database


app = Flask(__name__)
app.config['SECRET_KEY'] = 'guzinibambini'
Database.create_article_table()

# Создаем по умолчанию папку 'uploads/' для загрузки картинок
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    # POST-запрос
    user_name = request.form.get("user_name")
    email = request.form.get("email")
    password = request.form.get("password")
    password_repeat = request.form.get("password_repeat")

    if not user_name:
        flash("Имя пользователя (user_name) не может быть пустым!")
        # return redirect(url_for('register'))
        return redirect(request.url)

    if not email:
        flash("Электронная почта не может быть пустой!")
        return redirect(request.url)

    if not password:
        flash("Пароль не может быть пустым!")
        return redirect(request.url)

    if not password_repeat:
        flash("Повторите пароль!")
        return redirect(request.url)
    
    if password != password_repeat:
        flash("Пароли не совпадают!")
        return redirect(request.url)

    return redirect(url_for('index'))


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static/img'),
        'favicon.ico',
        mimetype="image/vnd.microsoft.icon"
    )


@app.route("/article/<title>")
def get_article(title):
    article = Database.find_article_by_title(title)
    if article is None:
        return "<h1>Такой статьи не существует!</h1>"

    return render_template(
        "article.html",
        article=article
        )


@app.route("/create_article", methods=["GET", "POST"])
def create_article():
    if request.method == "GET":
        return render_template('create_article.html', error=request.args.get("error"))
    
    # Далее обработка POST-запроса
    title = request.form.get("title")
    content = request.form.get("content")
    image = request.files.get("photo")
    
    if image is not None and image.filename:
        image_path = image.filename
        # Костыль: может вызвать проблемы с сохранением
        # картинок в папку
        image.save(app.config["UPLOAD_FOLDER"] + image_path)
    else:
        image_path = None

    saved = Database.save(
        Article(title, content, image_path)
    )
    if not saved:
        return redirect(url_for('create_article', error=True))

    return redirect(url_for('index'))


@app.route("/delete_article/<id>", methods=["POST"])
def delete_article(id):
    if not Database.delete(id):
        abort(404, f"Article id {id} doesn't exist")
    
    return redirect(url_for('index'))


@app.route("/update_article/<id>", methods=["GET", "POST"])
def update_article(id):
    article = Database.find_article_by_id(id)
    if article is None:
        abort(404, f"Article id {id} doesn't exist")

    if request.method == "GET":
        return render_template("update_article.html", article=article)
    
    # Обработка POST-запроса
    title = request.form.get("title")
    if title is None:
        title = article.title

    content = request.form.get("content")
    if content is None:
        content = article.content

    image = request.files.get("photo")
    if image is not None and image.filename:
        # Если мы задали новую картинку для статьи,
        # ее надо сохранить в отдельную папку
        image_path = image.filename
        image.save(app.config["UPLOAD_FOLDER"] + image_path)

        filename = image_path
    else:
        # Если мы не задавали картинку для статьи,
        # то надо взять старую из объекта article
        filename = article.image

    Database.update(id, title, content, filename)
    return redirect(url_for('get_article', title=title))


@app.route("/")
@app.route("/index")
def index():
    articles = Database.get_all_articles()

    count_in_group = 4
    groups = []
    for i in range(0, len(articles), count_in_group): # 0, 4, 8, 12, ...
        groups.append(articles[i:i+count_in_group]) # [0:4], [4:8], [8:12], ...

    return render_template("index.html", groups=groups)


@app.route('/uploads/<filename>')
def uploaded_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


app.run(debug=True, port=8088)
