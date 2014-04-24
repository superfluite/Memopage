from sqlalchemy import Column,Integer,String,Date,ForeignKey,Table
from flask.ext.login import UserMixin
from database import Base

class User(UserMixin,Base):
	__tablename__='users'
	id=Column(Integer,primary_key=True)
	userid=Column(String)
	userpw=Column(String)
	
	def __repr__(self):
		return '<User %s>' % (self.userid)

class Memo(Base):
	__tablename__='memos'
	id=Column(Integer,primary_key=True)
	text=Column(String)
	writerid=Column(Integer)
	writetime=Column(String)
	important=Column(Integer)
	
	def __repr__(self):
		return '<Memo %s>' % (self.id)