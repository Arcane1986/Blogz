from flask import Flask,render_template,request,redirect,session,flash
from flask_sqlalchemy import SQLAlchemy
from config import username,port,password,host,database,secret_key
from datetime import datetime

app=Flask(__name__)
app.config['DEBUG']=True
app.config['SQLACLHEMY_ECHO']=True

connection_string= f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'


app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
db = SQLAlchemy(app)
db_session = db.session
app.secret_key = secret_key

class Blog(db.Model):
  blog_id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50))
  body = db.Column(db.String(1000))
  created_at = db.Column(db.DateTime, default=datetime.now())
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __init__(self,title,body,user):
    self.title = title
    self.body = body
    self.user = user

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), )
  password = db.Column(db.String(20))
  email = db.Column(db.String(40))
  blogs = db.relationship("Blog", backref = 'user')

  def __init__(self,username,password,email):
    self.username = username
    self.password = password
    self.email = email

@app.before_request
def require_login():
  allowed_routes = ['login','signup']
  if 'username' not in session and request.endpoint not in allowed_routes:
    return redirect('/login')

@app.route("/login", methods=["POST","GET"])
def login():
  if 'username' not in session:
    if request.method == 'POST':
      username = request.form.get('username')
      password = request.form.get('p-word')
      current_user = User.query.filter_by(username = username).first()
      if username == "" or password == "":
        flash('Username and/or password can not be blank','error')
        return render_template("login.html",username=username,session=session,errorimg="https://media2.giphy.com/media/147dUv9HLZy5Ak/giphy.gif")
      elif current_user and current_user.password == password:
        session['username']=username
        flash(f'Welcome {username}','welcome')
        return redirect("/mypage?errorimg=https://media3.giphy.com/media/ktAQNsUfigR1K/200w.webp")    
      else:
        flash("Username is not in the system or the password provided is incorrect.",'error')
        return render_template("login.html",username=username,session=session,errorimg="https://media2.giphy.com/media/147dUv9HLZy5Ak/giphy.gif")
    else:
      return render_template("login.html")
  else:
    return redirect('/mypage')

@app.route("/signup", methods=["POST","GET"])
def signup():
  if request.method == 'POST':
    username = request.form.get('user-name')
    password = request.form.get('password')
    verified_pw = request.form.get('verified-password')
    current_user = User.query.filter_by(username = username).first()
    email = request.form['e-mail']
    if not current_user and password == verified_pw and '@' in email and email.count('.') == 1 and password != "":
      new_user = User(username,password,email)
      db.session.add(new_user)
      db.session.commit()
      session['username']=username
      flash(f'Welcome {username}','welcome')
      return redirect("/mypage?errorimg=https://media3.giphy.com/media/ktAQNsUfigR1K/200w.webp")
    else:
      flash("The username, password or email is invalid. Please update the form and resubmit", 'error')
      return render_template('signup.html',username=username,session=session,email=email,errorimg="https://media2.giphy.com/media/147dUv9HLZy5Ak/giphy.gif")
  else:
    return render_template("signup.html")

@app.route("/mypage")
def index():
  user = User.query.filter_by(username = session['username']).first()
  blogs = Blog.query.filter_by(user_id=user.id).order_by('blog_id desc').all()
  error = request.args.get('error')
  errorimg = request.args.get('errorimg')
  return render_template('main.html',blogs=blogs,error=error,errorimg=errorimg,session=session)

@app.route("/newpost", methods=['POST','GET'])
def newpost():
  if request.method == 'POST':
    title = request.form.get('title')
    body = request.form.get('body')
    userid = User.query.filter_by(username=session['username']).first()
    new_blog = Blog(title,body,userid)
    db.session.add(new_blog)
    db.session.commit()
    return redirect("/mypage")
  else:
    return render_template('newpost.html')

@app.route("/blog")
def individual_post():
  id = request.args.get('id')
  blog = Blog.query.get(id)
  if not blog:
    return redirect("/?error=This Blog does not exist")
  return render_template('blog.html', blog = blog)

@app.route('/logout')
def logout():
  del session['username']
  return redirect('/')

@app.route('/')
def all_blogs():
  blogz = Blog.query.order_by('blog_id desc').all()
  error = request.args.get('error')
  return render_template('main.html',blogs=blogz,session=session,error=error)

@app.route('/edit', methods=['POST','GET'])
def edit():
    if request.method == 'GET':
      id = request.args.get('id')
      blog = Blog.query.get(id)
      if blog.user.username == session['username']:
        if not blog:
          return redirect("/?error=This Blog does not exist")
        return render_template('edit.html', blog = blog)
      else:
        return redirect('/?error=Can not edit blogs which you do not own.')
    else:
      blog = Blog.query.get(id)
      if blog.user.username == session['username']:
        title = request.form.get('title')
        body = request.form.get('body')
        id = request.form.get('id')
        blog.body = body
        blog.title = title
        db.session.commit()
        return redirect('/mypage')
      else:
        redirect('/')

  

  
if __name__ == "__main__":
    db.create_all()
    app.run()