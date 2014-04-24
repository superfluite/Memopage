#imports
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash
from flask.ext.login import LoginManager,login_user,logout_user,login_required,session,current_user
from config import SECRET_KEY
from database import db_session
from sqlalchemy import desc
from models import *
import os
import sqlite3
import time

app=Flask(__name__)
login_manager=LoginManager()
app.secret_key=SECRET_KEY
login_manager.init_app(app)
login_manager.login_view="login"
now=time.localtime()

@login_manager.user_loader
def load_user(id):
	return db_session.query(User).get(int(id))

@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/main')
def main():
	if current_user!=None:
		memos=db_session.query(Memo).filter_by(writerid=current_user.id).order_by(desc(Memo.id)).all()
	return render_template('main.html',memos=memos)
	
@app.route('/login',methods=['GET','POST'])
def login():
	error=None
	if request.method=='POST':
		user=db_session.query(User).filter_by(userid=request.form['userid']).first()
		if user==None:
			error='Invalid ID! Please try again!'
		elif request.form['userpw']!=user.userpw:
			error='Invalid PW! Please try again!'
		else:
			session['logged_in']=True
			login_user(user)
			flash('Successfully logged in! XD')
			return redirect(url_for('main'))
	return render_template('login.html',error=error)

@app.route('/logout')
@login_required
def logout():
	session.pop('logged_in',None)
	logout_user()
	flash('Good bye! :D')
	return redirect(url_for('login'))
	
@app.route('/signup',methods=['GET','POST'])
def signup():
	error=None
	if request.method=='POST':
		user_check=db_session.query(User).filter_by(userid=request.form['userid']).first()
		if user_check!=None:
			error='User name already taken! Choose another!'
		else:
			user=User(userid=request.form['userid'],userpw=request.form['userpw'])
			db_session.add(user)
			db_session.commit()
			flash('Successfully signed up! Now log in!')
			return redirect(url_for('login'))
	return render_template('signup.html',error=error)

@app.route('/writememo',methods=['GET','POST'])
@login_required
def writememo():
	error=None
	if request.method=='POST':
		memo_check=request.form['text']
		if memo_check==None:
			error='This is blank memo! You have to write something!'
		else:
			time="%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year,now.tm_mon,now.tm_mday,now.tm_hour,now.tm_min,now.tm_sec)
			new_memo=Memo(text=request.form['text'],writerid=current_user.id,writetime=time)
			db_session.add(new_memo)
			db_session.commit()
			return redirect(url_for('main'))
	return render_template('writememo.html')

@app.route('/delmemo/<num>')
@login_required
def delmemo(num):
	poor_memo=db_session.query(Memo).filter_by(id=num).first()
	db_session.delete(poor_memo)
	db_session.commit()
	return redirect(url_for('main'))
	
@app.route('/editmemo/<num>',methods=['GET','POST'])
@login_required
def editmemo(num):
	fix_memo=db_session.query(Memo).filter_by(id=num).first()
	if request.method=='POST':
		memo_check=request.form['text']
		if memo_check==None:
			error='This is blank memo! You have to write something!'
		else:
			time="%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year,now.tm_mon,now.tm_mday,now.tm_hour,now.tm_min,now.tm_sec)
			fix_memo.text=request.form['text']
			fix_memo.writetime=time
			db_session.commit()
			return redirect(url_for('main'))
	return render_template('editmemo.html',fix_memo=fix_memo)

@app.route('/withdraw')
@login_required
def withdraw():
	return render_template('withdraw.html')
	
@app.route('/delaccount')
@login_required
def delaccount():
	poor_memo=db_session.query(Memo).filter_by(writerid=current_user.id).first()
	while poor_memo!=None:
		db_session.delete(poor_memo)
		db_session.commit()
		poor_memo=db_session.query(Memo).filter_by(writerid=current_user.id).first()
	poor_user=db_session.query(User).filter_by(id=current_user.id).first()
	session.pop('logged_in',None)
	logout_user()
	db_session.delete(poor_user)
	db_session.commit()
	return redirect(url_for('index'))
	
@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()
	
if __name__=='__main__':
	app.debug=True
	port=int(os.environ.get('PORT',5000))
	app.run(host='0.0.0.0',port=port)