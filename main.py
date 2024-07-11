from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import random 

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)


class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    views = db.Column(db.Integer, default=0)
    burn = db.Column(db.Boolean, default=False)
    poster_name = db.Column(db.String(32), default='Anonymous')
    title = db.Column(db.String(32))
    posted_at = db.Column(db.DateTime, server_default=db.func.now())

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/paste', methods=['GET', 'POST'])
def paste():
    if request.method == 'POST':
        content = request.form.get('content')
        poster_name = request.form.get('poster_name')
        burn = request.form.get('burn')
        if burn == 'on':
            burn = True
        else:
            burn = False
        id = random.randint(1000000, 9999999)
        title = request.form.get('title')
        if not content or not poster_name or not title:
            return render_template("error.html", message="Missing required fields")
        paste = Paste(content=content, poster_name=poster_name, burn=burn, title=title, id=id)  
        db.session.add(paste)
        db.session.commit()
        url = f'/paste/{paste.id}'
        return redirect(url)

    if request.method == 'GET':
        return redirect(url_for('home'))
    
@app.route('/paste/<int:id>')
def view_paste(id):
    paste = Paste.query.get(id)
    if not paste:
        return render_template("error.html", message="Paste not found")
    paste.views += 1
    db.session.commit()
    if paste.burn:
        if paste.views > 2:
            db.session.delete(paste)
            db.session.commit()
            return render_template("error.html", message="Paste has been burned")
    return render_template('paste.html', paste=paste)
    
if __name__ == '__main__':
    app.run()
