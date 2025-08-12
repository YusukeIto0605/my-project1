import os
import uuid
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import asc, desc, or_

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = \
  "{dialect}+{driver}://{user}:{password}@{host}/{database}?charset=utf8".format(
    dialect="mysql",
    driver="pymysql",
    user="books",
    password="books",
    host="127.0.0.1",
    port="3307",
    database="books"
  )

app.config['SQLALCHEMY_DATABASE_URI'] = \
  "{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}?charset=utf8".format(
    dialect="mysql",
    driver="pymysql",
    user="books",
    password="books",
    host="127.0.0.1",
    port="3307",
    database="books"
  )

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

db = SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    タイトル = db.Column(db.String(100))
    著者 = db.Column(db.String(100))
    出版年 = db.Column(db.Integer)
    ジャンル = db.Column(db.String(50))
    状態 = db.Column(db.String(20))
    概要 = db.Column(db.Text)

    images = db.relationship('BookImage', backref='book', cascade='all, delete-orphan')

class BookImage(db.Model):
    __tablename__ = 'book_images'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    keyword = request.args.get("q", "").strip()
    sort_col = request.args.get("sort", "id")
    order = request.args.get("order", "asc")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    if request.method == "POST":
        タイトル = request.form.get("タイトル")
        著者 = request.form.get("著者")
        出版年 = request.form.get("出版年")
        ジャンル = request.form.get("ジャンル")
        状態 = request.form.get("状態")
        概要 = request.form.get("概要")

        new_book = Book(
            タイトル=タイトル,
            著者=著者,
            出版年=int(出版年) if 出版年 and 出版年.isdigit() else None,
            ジャンル=ジャンル,
            状態=状態,
            概要=概要
        )
        db.session.add(new_book)
        db.session.commit()

        files = request.files.getlist("images")
        for file in files:
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                img = BookImage(book_id=new_book.id, filename=filename)
                db.session.add(img)
        db.session.commit()

        flash("本を登録しました。")
        return redirect(url_for("index"))

    if sort_col not in Book.__table__.columns.keys():
        sort_col = "id"

    col = getattr(Book, sort_col)
    if order == "desc":
        col = desc(col)
    else:
        col = asc(col)

    query = Book.query

    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Book.タイトル.like(like_pattern),
                Book.著者.like(like_pattern),
                Book.ジャンル.like(like_pattern),
                Book.概要.like(like_pattern)
            )
        )

    query = query.order_by(col)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items
    columns = list(Book.__table__.columns.keys())

    return render_template(
        "wp.html",
        d=books,
        c=columns,
        keyword=keyword,
        sort_col=sort_col,
        order=order,
        pagination=pagination,
    )

@app.route("/delete")
def delete():
    book_id = request.args.get("id")
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        flash("本を削除しました。")
    else:
        flash("本が見つかりません。")
    return redirect(url_for("index"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    book = Book.query.get(id)
    if not book:
        return "指定された本が見つかりません", 404

    if request.method == "POST":
        book.タイトル = request.form.get("タイトル")
        book.著者 = request.form.get("著者")
        出版年 = request.form.get("出版年")
        if 出版年 and 出版年.isdigit():
            book.出版年 = int(出版年)
        book.ジャンル = request.form.get("ジャンル")
        book.状態 = request.form.get("状態")
        book.概要 = request.form.get("概要")

        files = request.files.getlist("images")
        for file in files:
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                img = BookImage(book_id=book.id, filename=filename)
                db.session.add(img)

        db.session.commit()
        flash("本を更新しました。")
        return redirect(url_for("index"))

    return render_template("edit.html", book=book)

if __name__ == '__main__':
    app.run()