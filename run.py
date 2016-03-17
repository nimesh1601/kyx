from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import jsonify
from wtforms import Form
from wtforms import BooleanField
from wtforms import TextField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms.fields.html5 import EmailField
from wtforms import validators
from form import *
from copy import deepcopy
from redis import Redis
import string
import random
import hashlib
import smtplib
import werkzeug
import datetime
import os

app=Flask(__name__)
app.secret_key='A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

m=[]
cglist=[]

import MySQLdb as mdb

db=mdb.connect('xcula-ent.chzrk3ubghro.ap-southeast-1.rds.amazonaws.com','xcula','16april2020','knowyourx')
cur=db.cursor()

rs=Redis('localhost')



def id_generator(size=5, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
	return ''.join(random.choice(chars) for _ in range(size))
	
def passwordsend(receiver,mess):
	sender = 'knowyourx@gmail.com'
	receivers = []
	receivers.append(receiver)
	message = """From: %s
To: %s
Subject: KnowYourVIT Confirmation mail
	
Thank you for registring with Know Your Vit.
We appreciate your interest and promise you the best information from the most trustworthy sources around VIT.
This is just a baby step we plan to make it bigger and better each day.
You are just one step away to access all the information available on our forum.
Kindly click on the following link to verify your E-Mail account and to complete the last steps of setting up your account:
Link- %s







This is a system generated mail.Kindly do not reply to it.
For any assisstance or queries please direct your mails to abc@xyz.com

Please ignore this mail if you do not wish to register with Know Your Vit 
 
	
	""" % (sender, ", ".join(receivers),mess)
	
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login('knowyourx', '27dec2015')
	server.sendmail(sender, receivers, message)
	server.close()
	print 'successfully sent the mail'
	
def cgpacal(name,type,credits,q1,q1a,q2,q2a,q3,q3a,assign,assigna,c1,c1a,c2,c2a,min,max,labi,labex,cg):
	lab=labi+labex
	st=q1+q2+q3+assign+(0.3*(c1+c2))
	st=1.95*st
	sta=q1a+q2a+q3a+assigna+(0.3*(c1a+c2a))
	sta=1.95*sta
	if type=='ETH':
		st=(((credits-1)*st)+lab)/credits
		sta=(((credits-1)*sta)+lab)/credits
	if cg>8:
		if type=='LAB':
			if lab>=90:
				res='S'
			elif lab>=80:
				res='A'
			elif lab>=70:
				res='B'
			elif lab>=60:
				res='C'
			elif lab>=55:
				res='D'
			elif lab>=50:
				res='E'
			else:
				res='F'
		else:
			if st>sta+1.5*(min):
				res='S'
			elif st>sta+0.5*(min):
				res='A'
			elif st>sta-0.5*(min):
				res='B'
			elif st>sta-1.0*(min):
				res='C'
			elif st>sta-1.5*(min):
				res='D'
			elif st>sta-2.0*(min):
				res='E'
			else:
				res='F'
	else:
		if type=='LAB':
			if lab>=90:
				res='S'
			elif lab>=80:
				res='A'
			elif lab>=70:
				res='B'
			elif lab>=60:
				res='C'
			elif lab>=55:
				res='D'
			elif lab>=50:
				res='E'
			else:
				res='F'
		else:
			if st>sta+1.5*(max):
				res='S'
			elif st>sta+0.5*(max):
				res='A'
			elif st>sta-0.5*(max):
				res='B'
			elif st>sta-1.0*(max):
				res='C'
			elif st>sta-1.5*(max):
				res='D'
			elif st>sta-2.0*(max):
				res='E'
			else:
				res='F'
	if type=='ETH':
		if lab<50:
			res='F'
	return res
	
def cgcal(cgcala):
	cgcalsum=0
	cgcalcred=0
	for i in cgcala:
		if i[2]=='S':
			i[2]=10
		elif i[2]=='A':
			i[2]=9
		elif i[2]=='B':
			i[2]=8
		elif i[2]=='C':
			i[2]=7
		elif i[2]=='D':
			i[2]=6
		elif i[2]=='E':
			i[2]=5
		else:
			i[2]=0
		cgcalsum=cgcalsum+(i[1]*i[2])
		cgcalcred=cgcalcred+i[1]
	cgcalcred=float(cgcalcred)
	cgf=round(cgcalsum/cgcalcred,2)
	return cgf
	
def allowed_file(file):
	if file.rsplit('.',1)[1] in ['jpg']:
		return 1
	else:
		return 0
	
@app.route('/')
def home():
	if 'username' in session:
		return redirect('/events')
	if 'club' in session:
		return redirect(url_for('clubs',clubid=0))
	form1=Signup(request.form)
	form2=Signin(request.form)
	return render_template('home.html',form1=form1,form2=form2)

@app.route('/sup',methods=['GET','POST'])
def sup():
	if 'username' in session:
		return redirect('/events')
	if 'club' in session:
		return redirect(url_for('clubs',clubid=0))
	form=Signup(request.form)
	if request.method=='POST' and form.validate():
		n=form.username.data
		r=form.reg.data
		e=form.email.data
		c=form.college.data
		p=id_generator()
		p=n+p
		pg=hashlib.md5()
		pg.update(p)
		p=pg.hexdigest()
		ps=url_for('passw',passhash=p)
		passwordsend(e,ps)
		with db:
			cur.execute('insert into login values(%s,%s,%s,%s,now(),0,"",%s,"")',(n,p,r,e,c))
			return render_template('supcomp.html')		
	return render_template('sup.html',form=form)
	
@app.route('/sin',methods=['GET','POST'])
def sin():
	if 'username' in session:
		return redirect(url_for('events'))
	if 'club' in session:
		return redirect(url_for('clubs',clubid=0))
	form=Signin(request.form)
	if request.method=='POST' and form.validate():
		with db:
			cur.execute('select username from login where email=%s',(form.email.data,))
			ld=cur.fetchall()
			session['username']=ld[0][0]
			return redirect(url_for('events'))
	if request.args.get('access')=='1':
		return render_template('sin.html',access=1,form=form)
	return render_template('sin.html',form=form)
	
# @app.route('/prof')
# def prof():
	# if 'username' in session:
		# if session['username']=='VinayakaB' or session['username']=='NimeshK':
			# with db:
				# cur.execute('select count(*) from login')
				# tusers=cur.fetchall()
				# cur.execute('select count(*) from login where activ=1')
				# ausers=cur.fetchall()
			# return render_template('profadmin.html',tusers=tusers,ausers=ausers)
		# with db:
			# cur.execute('select username,reg,email from login where username=%s',(session['username'],))
			# ld=cur.fetchall()
			# cur.execute('select * from facrev,rev where facrev.username=%s and facrev.revid=rev.revid and likes=1',(session['username'],))
			# myrev=cur.fetchall()
			# cur.execute('select * from facrev,rev where facrev.username=%s and facrev.revid=rev.revid and likes=2',(session['username'],))
			# myrevd=cur.fetchall()
		# return render_template('prof.html',users=ld,myrev=len(myrev),myrevd=len(myrevd))
	# return redirect(url_for('sin',access=1))
	
@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username',None)
		return redirect(url_for('home'))
	return redirect('/')
	
@app.route('/passw/<passhash>',methods=['GET','POST'])
def passw(passhash):
	if 'club' in session or 'username' in session:
		return redirect(url_for('home'))
	form=passchange(request.form)
	with db:
		cur.execute('select pass from login where pass=%s',(passhash,))
		ld1=cur.fetchall()
		if ld1:
			if request.method=='POST' and form.validate():
				with db:
					cur.execute('select username from login where pass=%s',(passhash,))
					ld=cur.fetchall()
					n=ld[0][0]
				p=form.password.data
				p=n+p
				pg=hashlib.md5()
				pg.update(p)
				p=pg.hexdigest()
				with db:
					cur.execute('update login set pass=%s where pass=%s',(p,passhash))
					cur.execute('update login set activ=1 where pass=%s',(p,))
					return redirect('/sin')
			return render_template('passchange.html',form=form,passhash=passhash)
		return redirect(url_for('home'))
		
@app.route('/passclub/<passhash>',methods=['GET','POST'])
def passclub(passhash):
	if 'club' in session or 'username' in session:
		return redirect(url_for('home'))
	with db:
		cur.execute('select * from clubs where pass1=%s or pass2=%s',(passhash,passhash))
		cdata=cur.fetchall()
		if not cdata:
			return redirect(url_for('home'))
		else:
			if request.method=='POST':
				password=request.form['password']
				repass=request.form['repass']
				if password!=repass:
					return render_template('passclub.html',passhash=passhash,error='Password not same')
				else:
					password=str(cdata[0][1])+str(password)
					pg=hashlib.md5()
					pg.update(password)
					password=pg.hexdigest()
					cur.execute('update clubs set pass1=%s where pass1=%s',(password,passhash))
					cur.execute('update clubs set pass2=%s where pass2=%s',(password,passhash))
					return redirect('/sin_club')
			return render_template('passclub.html',passhash=passhash,error='')

@app.route('/cpass',methods=['GET','POST'])
def cpass():
	if 'username' in session:
		if request.method=='POST':
			password=request.form['password']
			cpassword=request.form['cpassword']
			repassword=request.form['repassword']
			password=session['username']+password
			pg=hashlib.md5()
			pg.update(password)
			password=pg.hexdigest()
			with db:
				cur.execute('select * from login where pass=%s and username=%s',(password,session['username']))
				cpassdata=cur.fetchall()
				if cpassdata:
					if cpassword==repassword:
						cpassword=session['username']+cpassword
						pg1=hashlib.md5()
						pg1.update(cpassword)
						cpassword=pg1.hexdigest()
						cur.execute('update login set pass=%s where username=%s',(cpassword,session['username']))
						return redirect(url_for('home'))
					else:
						return render_template('cpass.html',error="Passwords don't Match")	
				else:
					return render_template('cpass.html',error='Wrong Password')	
		return render_template('cpass.html',error='')	
	else:
		return redirect(url_for('home'))
		
@app.route('/cpassclub',methods=['GET','POST'])
def cpassclub():
	if 'club' in session:
		if request.method=='POST':
			password=request.form['password']
			cpassword=request.form['cpassword']
			repassword=request.form['repassword']
			with db:
				cur.execute('select name from clubs where cid=%s',(session['club'],))
				cname=cur.fetchall()[0][0]
				password=cname+password
				pg=hashlib.md5()
				pg.update(password)
				password=pg.hexdigest()
				cur.execute('select * from clubs where pass1=%s or pass2=%s',(password,password))
				cpassdata=cur.fetchall()
				if cpassdata:
					if cpassword==repassword:
						cpassword=cname+cpassword
						pg1=hashlib.md5()
						pg1.update(cpassword)
						cpassword=pg1.hexdigest()
						cur.execute('update clubs set pass1=%s where pass1=%s',(cpassword,password))
						cur.execute('update clubs set pass2=%s where pass2=%s',(cpassword,password))
						return redirect(url_for('home'))
					else:
						return render_template('cpassclub.html',error="Passwords Don't Match")	
				else:
					return render_template('cpassclub.html',error='Wrong Password')	
		return render_template('cpassclub.html',error='')	
	else:
		return redirect(url_for('home'))
	
@app.route('/fpass',methods=['GET','POST'])
def fpass():
	if 'username' in session or 'club' in session:
		return redirect(url_for('home'))
	form=fpassw(request.form)
	if request.method=='POST' and form.validate():
		with db:
			cur.execute('select pass from login where email=%s',(form.email.data,))
			ld=cur.fetchall()
			p=ld[0][0]
		e=form.email.data
		ps=url_for('passw',passhash=p)
		passwordsend(e,ps)
		return redirect(url_for('home'))
	return render_template('fpass.html',form=form)
	
@app.route('/fpassclub',methods=['GET','POST'])
def fpassclub():
	if 'username' in session or 'club' in session:
		return redirect(url_for('home'))
	else:
		if request.method=='POST':
			mailid=request.form['email']
			with db:
				cur.execute('select clubid1,pass1 from clubs where clubid1=%s',(mailid,))
				maildetails=list(cur.fetchall())
				cur.execute('select clubid2,pass2 from clubs where clubid2=%s',(mailid,))
				maildetails.extend(list(cur.fetchall()))
				if maildetails:
					p=maildetails[0][1]
					ps=url_for('passclub',passhash=p)
					passwordsend(maildetails[0][0],ps)
					return redirect(url_for('home'))
				else:
					return render_template('fpassclub.html',error='No Account assosciated with this Mail')
		return render_template('fpassclub.html',error='')	

@app.route('/sin_club',methods=['GET','POST'])
def sin_club():
	if 'username' in session or 'club' in session:
		return redirect('/')
	else:
		if request.method=='POST':
			mailid=request.form['email']
			password=request.form['password']
			with db:
				cur.execute('select name from clubs where clubid1=%s or clubid2=%s',(mailid,mailid))
				cname=cur.fetchall()
				if cname:
					password=cname[0][0]+password
				else:
					return render_template('sinclub.html',error='Wrong Email or Password')
			pg=hashlib.md5()
			pg.update(password)
			password=pg.hexdigest()
			with db:
				cur.execute('select cid from clubs where clubid1=%s and pass1=%s',(mailid,password))
				login_details=cur.fetchall()
				if login_details:
					session['club']=login_details[0][0]
					return redirect(url_for('home'))
				else:
					cur.execute('select cid from clubs where clubid2=%s and pass2=%s',(mailid,password))
					login_details=cur.fetchall()
					if login_details:
						session['club']=login_details[0][0]	
						return redirect(url_for('home'))
					else:
						return render_template('sinclub.html',error='Wrong Email or Password')
	return render_template('sinclub.html',error='')
	
@app.route('/clublogout')
def clublogout():
	if 'club' in session:
		session.pop('club',None)
	return redirect(url_for('home'))
	
@app.route('/clubs/<int:clubid>')
def clubs(clubid):
	if clubid==0:
		if 'club' in session:
			clubid=session['club']
			with db:
				cur.execute('select name,college,views,cid,contact1,contact2 from clubs where cid=%s',(clubid,))
				clubdata=list(cur.fetchall()[0])
				cdescr=open('static/clubs/'+str(clubdata[3])+'.txt','r')
				clubdata[3]=cdescr.read()
				cdescr.close()
				cur.execute('select cname from colleges where college=%s',(clubdata[1],))
				clubdata[1]=cur.fetchall()[0][0]
				clubmembers=[]
				for i in range(1,11):
					if os.path.exists('static/clubs/'+str(clubid)+'/member'+str(i)+'.txt'):
						cmember=open('static/clubs/'+str(clubid)+'/member'+str(i)+'.txt','r')
						clubmembers.append(cmember.read().split('\n'))
						cmember.close()
					else:
						break
				cur.execute('select * from events where cid=%s and esdate>=%s',(clubid,datetime.datetime.now().strftime('%Y-%m-%d')))
				edata=cur.fetchall()
				evdata=[]
				for i in edata:
					evdata.append(list(i))
				for i in evdata:	
					file_name=str(i[1])+'_descr.txt'
					event_descr=open('static/events/'+file_name,'r')
					i[8]=event_descr.read()
					event_descr.close()	
			return render_template('clubprofile.html',cdata=clubdata,clubmembers=clubmembers,evdata=evdata)
		else:
			return redirect('/')
	else:
		ip=request.remote_addr
		ip=ip+'/clubs/'+str(clubid)
		if rs.get(ip):
			rs.expire(ip,1200)
		else:
			rs.set(ip,1)
			rs.expire(ip,1200)
			if rs.hget('/clubs/'+str(clubid),'views'):
				rs.hincrby('/clubs/'+str(clubid),'views',1)
			else:
				rs.hset('/clubs/'+str(clubid),'views',1)
		print rs.hget('/clubs/'+str(clubid),'views')
		form1=Signup(request.form)
		form2=Signin(request.form)
		with db:
			cur.execute('select name,college,views,cid,contact1,contact2 from clubs where cid=%s',(clubid,))
			clubdata=list(cur.fetchall()[0])
			cdescr=open('static/clubs/'+str(clubdata[3])+'.txt','r')
			clubdata[3]=cdescr.read()
			cdescr.close()
			cur.execute('select cname from colleges where college=%s',(clubdata[1],))
			clubdata[1]=cur.fetchall()[0][0]
			clubmembers=[]
			for i in range(1,11):
				if os.path.exists('static/clubs/'+str(clubid)+'/member'+str(i)+'.txt'):
					cmember=open('static/clubs/'+str(clubid)+'/member'+str(i)+'.txt','r')
					clubmembers.append(cmember.read().split('\n'))
					cmember.close()
				else:
					break
			cur.execute('select * from events where cid=%s and esdate>=%s',(clubid,datetime.datetime.now().strftime('%Y-%m-%d')))
			edata=cur.fetchall()
			evdata=[]
			for i in edata:
				evdata.append(list(i))
			for i in evdata:	
				file_name=str(i[1])+'_descr.txt'
				event_descr=open('static/events/'+file_name,'r')
				i[8]=event_descr.read()
				event_descr.close()
		if 'club' in session:
			return render_template('clubs.html',form1=form1,form2=form2,cdata=clubdata,clubmembers=clubmembers,evdata=evdata,club=session['club'])
		if 'username' in session:
			return render_template('clubs.html',form1=form1,form2=form2,cdata=clubdata,clubmembers=clubmembers,evdata=evdata,user=session['username'])
		else:
			return redirect(url_for('home'))
		
@app.route('/clubcontatct1',methods=['POST'])
def clubcontact1():
	if 'club' in session:
		contact=request.form['contact']
		if not contact:
			return redirect(url_for('home'))
		if contact[0]=='+':
			contact=contact[3:]
		if contact[0]=='-':
			contact=contact[1:]
		with db:
			cur.execute('update clubs set contact1=%s where cid=%s',(contact,session['club']))
	return redirect(url_for('home'))
			
@app.route('/clubcontatct2',methods=['POST'])
def clubcontact2():
	if 'club' in session:
		contact=request.form['contact']
		if not contact:
			return redirect(url_for('home'))
		with db:
			cur.execute('update clubs set contact2=%s where cid=%s',(contact,session['club']))
	return redirect(url_for('home'))
			
@app.route('/clubabout',methods=['POST'])
def clubabout():
	if 'club' in session:
		about=request.form['about']
		cdescr=open('static/clubs/'+str(session['club'])+'.txt','w')
		cdescr.write(about)
		cdescr.close()
	return redirect(url_for('home'))
		
@app.route('/event_insert',methods=['POST'])
def event_insert():
	if 'club' in session:
		ename=request.form['name']
		etype=request.form['type']
		venue=request.form['venue']
		regfee=request.form['regfee']
		cont=request.form['contact']
		reglink=request.form['reglink']
		descr=request.form['descr']
		esdate=request.form['edate']
		eedate=esdate
		estime=request.form['etime']
		eetime=estime
		poster=request.files['poster']
		if poster:
			if allowed_file(poster.filename):	
				posters=1
			else:
				posters=0
		else:
			posters=0
		with db:
			cur.execute('insert into events values(%s,"",%s,%s,%s,%s,%s,%s,"",%s,%s,%s,%s,%s,"")',(session['club'],ename,etype,venue,regfee,cont,reglink,esdate,eedate,estime,eetime,posters))
			cur.execute('select evid from events where cid=%s and esdate=%s and ename=%s',(session['club'],esdate,ename))
			evid=str(cur.fetchall()[0][0])
			description=open('static/events/'+evid+'_descr.txt','w')
			description.write(descr)
			description.close()
			if posters==1:
				poster.save(os.path.join('static\uploads\events',evid+'.jpg'))	
			return redirect(url_for('home'))

@app.route('/events')
def events():
	form1=Signup(request.form)
	form2=Signin(request.form)
	if 'username' in session:
		return render_template('events.html',user=session['username'],form1=form1,form2=form2)
	if 'club' in session:
		return render_template('events.html',club=session['club'],form1=form1,form2=form2)
	return redirect(url_for('home'))

@app.route('/eventdata')
def eventdata():
	sdate=request.args.get('sdate')
	edate=request.args.get('edate')
	if sdate:
		sdate=datetime.datetime.strptime(sdate,"%m/%d/%Y").strftime('%Y-%m-%d')
	else:
		sdate=datetime.datetime.now().strftime('%Y-%m-%d')
	if edate:
		edate=datetime.datetime.strptime(edate,"%m/%d/%Y").strftime('%Y-%m-%d')
	with db:
		edata=[]
		cur.execute('select * from clubs')
		cdata_1=cur.fetchall()
		cdata={}
		for i in cdata_1:
			cdata[i[0]]=i[1]
		if edate:
			cur.execute('select * from events where esdate>=%s and esdate<=%s',(sdate,edate))
		else:
			cur.execute('select * from events where esdate>=%s',(sdate,))
		etdata=list(cur.fetchall())
		for i in etdata:
			edata.append(list(i))
		for i in edata:
			i[0]=cdata[i[0]]
			if i[3]=='Workshop':
				i[3]=1
			elif i[3]=='Event':
				i[3]=2
			elif i[3]=='CC':
				i[3]=3
			elif i[3]=='Others':
				i[3]=4
			i[9]=str(i[9])
			i[10]=str(i[10])
			i[11]=str(i[11])
			i[12]=str(i[12])
			cur.execute('select college from clubs where name=%s',(i[0],))
			i.append(cur.fetchall()[0][0])
	return jsonify(edata=edata)
	
@app.route('/eventdisp')
def eventdisp():
	sdate=request.args.get('sdate')
	edate=request.args.get('edate')
	fee1=request.args.get('fee1')
	fee2=request.args.get('fee2')
	fee3=request.args.get('fee3')
	fee4=request.args.get('fee4')
	fee5=request.args.get('fee5')
	etype1=request.args.get('etype1')
	etype2=request.args.get('etype2')
	ekind=request.args.get('ekind')
	if sdate:
		sdate=datetime.datetime.strptime(sdate,"%m/%d/%Y").strftime('%Y-%m-%d')
	else:
		sdate=datetime.datetime.now().strftime('%Y-%m-%d')
	if edate:
		edate=datetime.datetime.strptime(edate,"%m/%d/%Y").strftime('%Y-%m-%d')
	with db:
		edata=[]
		cur.execute('select * from clubs')
		cdata_1=cur.fetchall()
		cdata={}
		for i in cdata_1:
			cdata[i[0]]=i[1]
		if edate:
			cur.execute('select * from events where esdate>=%s and esdate<=%s',(sdate,edate))
		else:
			cur.execute('select * from events where esdate>=%s',(sdate,))
		etdata=list(cur.fetchall())
		if fee1=='false' and fee2=='false' and fee3=='false' and fee4=='false' and fee5=='false':
			fee1='true'
			fee2='true'
			fee3='true'
			fee4='true'
			fee5='true'
		for i in etdata:
			edata.append(list(i))
		for i in range(len(edata)-1,-1,-1):
			if edata[i][5]==0:
				if fee1=='false':
					edata.pop(i)
			elif edata[i][5]<=50:
				if fee2=='false':
					edata.pop(i)
			elif edata[i][5]<=100:
				if fee3=='false':
					edata.pop(i)
			elif edata[i][5]<=500:
				if fee4=='false':
					edata.pop(i)
			else:
				if fee5=='false':
					edata.pop(i)
		for i in range(len(edata)-1,-1,-1):
			if ekind=='0':
				break
			elif ekind=='1':
				if edata[i][3]!='Workshop':
					edata.pop(i)
			elif ekind=='2':
				if edata[i][3]!='Event':
					edata.pop(i)
			elif ekind=='3':
				if edata[i][3]!='CC':
					edata.pop(i)
			else:
				if edata[i][3]!='Others':
					edata.pop(i)
		for i in edata:			
			i[9]=str(i[9])
			i[10]=str(i[10])
			i[11]=str(i[11])
			i[12]=str(i[12])
			file_name=str(i[1])+'_descr.txt'
			event_descr=open('static/events/'+file_name,'r')
			i[8]=event_descr.read()
			event_descr.close()
			if i[13]==0:
				i[13]='poster.jpg'
			else:
				pg=hashlib.md5()
				pg.update(str(i[1]))
				i[13]=str(pg.hexdigest())+'.jpg'
			i.append(cdata[i[0]])
	return render_template('eventframe.html',edata=edata)

@app.route('/eventviewmore')
def eventviewmore():
	eid=request.args.get('eid')
	eid=eid[6:]
	ip=request.remote_addr
	ip=ip+'/events/'+eid
	if rs.get(ip):
		rs.expire(ip,1200)
	else:
		rs.set(ip,1)
		rs.expire(ip,1200)
		if rs.hget('/events/'+eid,'views'):
			rs.hincrby('/events/'+eid,'views',1)
		else:
			rs.hset('/events/'+eid,'views',1)
	print rs.hget('/events/'+eid,'views')
	return jsonify()
	
@app.route('/search')
def search():
	form1=Signup(request.form)
	form2=Signin(request.form)
	with db:
		cur.execute('select cid,name from clubs')
		cdata=cur.fetchall()
	if 'username' in session:
		return render_template('search.html',cdata=cdata)
	if 'club' in session:
		return render_template('search.html',cdata=cdata)
	else:
		return render_template('search.html',form1=form1,form2=form2,cdata=cdata)
		
# @app.route('/cgpacalc',methods=['GET','POST'])
# def cgpacalc():	
	# if 'username' in session:
		# if request.method=='POST':
			# name=request.form['name']
			# type=request.form['type']
			# credits=int(request.form['credits'])
			# if type!='LAB':
				# quiz1=float(request.form['quiz1'])
				# quiz1a=float(request.form['quiz1a'])
				# quiz2=float(request.form['quiz2'])
				# quiz2a=float(request.form['quiz2a'])
				# quiz3=float(request.form['quiz3'])
				# quiz3a=float(request.form['quiz3a'])
				# assign=float(request.form['assign'])
				# assigna=float(request.form['assigna'])
				# cat1=float(request.form['cat1'])
				# cat1a=float(request.form['cat1a'])
				# cat2=float(request.form['cat2'])
				# cat2a=float(request.form['cat2a'])
			# else:
				# quiz1=0
				# quiz1a=0
				# quiz2=0
				# quiz2a=0
				# quiz3=0
				# quiz3a=0
				# assign=0
				# assigna=0
				# cat1=0
				# cat1a=0
				# cat2=0
				# cat2a=0			
			# cg=float(request.form['cgpa'])	
			# sc=request.form.getlist('sc')
			# if type!='TH':
				# labi=float(request.form['labi'])
				# labex=float(request.form['labex'])
			# else:
				# labi=0
				# labex=0
			# if sc:
				# res=cgpacal(name,type,credits,quiz1,quiz1a,quiz2,quiz2a,quiz3,quiz3a,assign,assigna,cat1,cat1a,cat2,cat2a,10,11,labi,labex,cg)
			# else:
				# res=cgpacal(name,type,credits,quiz1,quiz1a,quiz2,quiz2a,quiz3,quiz3a,assign,assigna,cat1,cat1a,cat2,cat2a,13,15,labi,labex,cg)
			# if 'cgpa' in session:
				# del m[:]
				# del cglist[:]
				# for j in session['cgpa']:		
					# m.append(j)			
				# m.append([name,credits,res])
				# cglist.append(cgcal(deepcopy(m)))
				# session['cgpa']=m
			# else:
				# del m[:]
				# del cglist[:]
				# m.append([name,credits,res])
				# cglist.append(cgcal(deepcopy(m)))
				# session['cgpa']=m
			# return render_template('cgpa.html',res=res,m=m,cglist=cglist,sess=session['username'])
		# if 'cgpa' not in session:
			# del m[:]
			# del cglist[:]
			# return render_template('cgpa.html',m=m,cglist=cglist,sess=session['username'])
		# else:
			# if request.args.get('next')=='Reset':
				# session.pop('cgpa',None)
				# return redirect('/cgpacalc')
			# del m[:]
			# del cglist[:]
			# m.extend(session['cgpa'])
			# cglist.append(cgcal(deepcopy(m)))
			# return render_template('cgpa.html',m=m,cglist=cglist,sess=session['username'])
	# return redirect(url_for('sin',access=1))		
		

# @app.route('/qa_read')
# def qa_read():
	# if 'username' in session:
		# with db:
			# cur.execute('select uid from login where username=%s',(session['username'],))
			# uid=cur.fetchall()[0][0]
			# cur.execute('select tagid from user_tags where uid=%s',(uid,))
			# tagids=cur.fetchall()
			# answers=[]
			# ques=[]
			# for i in tagids:
				# cur.execute('select * from ques q,ans a where a.qid=q.qid and (tag1=%s or tag2=%s or tag3=%s or tag4=%s or tag5=%s or tag6=%s or tag7=%s or tag8=%s or tag9=%s or tag10=%s) and a.uid!=%s',(i[0],i[0],i[0],i[0],i[0],i[0],i[0],i[0],i[0],i[0],uid));
				# ques.append(cur.fetchall())
			# for i in ques:
				# for j in i:
					# if list(j) not in answers:
						# answers.append(list(j))
			# for i in answers:
				# if i[2]==0:
					# cur.execute('select username from login where uid=%s',(i[1],))
					# i[1]=cur.fetchall()[0][0]
				# else:
					# i[1]='Anonymous'
				# i.pop(2);
				# i.pop(14);
				# if i[17]==0:
					# cur.execute('select username from login where uid=%s',(i[16],))
					# i[16]=cur.fetchall()[0][0]
				# else:
					# i[16]='Anonymous'
				# i.pop(17)
				# i.pop(17)
				# i.pop(18)
				# tags=[]
				# for j in range(13,3,-1):
					# if i[j]!=0:
						# cur.execute('select tag from tags where tagid=%s',(i[j],))
						# tags.append(cur.fetchall()[0][0])
					# i.pop(j)
				# i.insert(4,tags)	
				# cur.execute('select count(*) from likes where type=1 and elemid=%s and likes=1',(i[6],))
				# i.append(cur.fetchall()[0][0])
				# cur.execute('select count(*) from likes where type=1 and elemid=%s and likes=2',(i[6],))
				# i.append(cur.fetchall()[0][0])
			# answers.sort(key=lambda answer:answer[9], reverse=True)	
			# return render_template('qa_read.html',answers=answers,username=session['username'])
	# return redirect(url_for('sin',access=1))

# @app.route('/qa_write')
# def qa_write():
	# if 'username' in session:
		# with db:
			# cur.execute('select uid from login where username=%s',(session['username'],))
			# uid=cur.fetchall()[0][0]
			# cur.execute('select tagid from user_tags where uid=%s',(uid,))
			# tagids=cur.fetchall()
			# ques=[]
			# questions=[]
			# for i in tagids:
				# cur.execute('select * from ques where (tag1=%s or tag2=%s or tag3=%s or tag4=%s or tag5=%s or tag6=%s or tag7=%s or tag8=%s or tag9=%s or tag10=%s) and uid!=%s',(i[0],i[0],i[0],i[0],i[0],i[0],i[0],i[0],i[0],i[0],uid));
				# questions.append(cur.fetchall())
			# for i in questions:
				# for j in i:
					# if list(j) not in ques:
						# ques.append(list(j))
			# for i in ques:
				# if i[2]==0:
					# cur.execute('select username from login where uid=%s',(i[1],))
					# i[1]=cur.fetchall()[0][0]
				# else:
					# i[1]='Anonymous'
				# i.pop(2)
				# i.pop(14)
				# cur.execute('select count(*) from ans where qid=%s',(i[0],))
				# i.append(cur.fetchall()[0][0])
				# tags=[]
				# for j in range(13,3,-1):
					# if i[j]!=0:
						# cur.execute('select tag from tags where tagid=%s',(i[j],))
						# tags.append(cur.fetchall()[0][0])
					# i.pop(j)
				# i.insert(4,tags)				
			# ques.sort(key=lambda question:question[5], reverse=True)	
			# return render_template('qa_write.html',ques=ques)	
	# return redirect(url_for('sin',access=1))
	
# @app.route('/qa_like')
# def qa_like():
	# if 'username' in session:
		# type=request.args.get('type')
		# id=request.args.get('id')
		# with db:
			# cur.execute('select uid from login where username=%s',(session['username'],))
			# uid=cur.fetchall()[0][0]
			# if type=='answer':
				# type=1
			# elif type=='question':
				# type=0
			# else:
				# type=2
			# cur.execute('select likes from likes where type=%s and elemid=%s and uid=%s',(type,id,uid))
			# likedata=cur.fetchall()
			# if likedata:
				# if likedata[0][0]==1:
					# cur.execute('delete from likes where type=%s and elemid=%s and uid=%s',(type,id,uid))
				# else:
					# cur.execute('update likes set likes=1 where type=%s and elemid=%s and uid=%s',(type,id,uid))
			# else:
				# cur.execute('insert into likes values(%s,%s,%s,0,1)',(type,id,uid))
		# return jsonify()
	# return redirect(url_for('home'))	

# @app.route('/qa_dislike')
# def qa_dislike():
	# if 'username' in session:
		# type=request.args.get('type')
		# id=request.args.get('id')
		# with db:
			# cur.execute('select uid from login where username=%s',(session['username'],))
			# uid=cur.fetchall()[0][0]
			# if type=='answer':
				# type=1
			# elif type=='question':
				# type=0
			# else:
				# type=2
			# cur.execute('select likes from likes where type=%s and elemid=%s and uid=%s',(type,id,uid))
			# likedata=cur.fetchall()
			# if likedata:
				# if likedata[0][0]==2:
					# cur.execute('delete from likes where type=%s and elemid=%s and uid=%s',(type,id,uid))
				# else:
					# cur.execute('update likes set likes=2 where type=%s and elemid=%s and uid=%s',(type,id,uid))
			# else:
				# cur.execute('insert into likes values(%s,%s,%s,0,2)',(type,id,uid))
		# return jsonify()
	# return redirect(url_for('home'))
	
# @app.route('/qa_comm')
# def qa_comm():
	# if 'username' in session:
		# type=request.args.get('type')
		# id=request.args.get('id')
		# comm=request.args.get('comm')
		# with db:
			# if type=='answer':
				# type=1
			# else:
				# type=0
			# cur.execute('select uid from login where username=%s',(session['username'],))
			# uid=cur.fetchall()[0][0]
			# cur.execute('insert into comm values("",0,%s,0,%s,%s,%s,now())',(uid,type,id,comm))
			# return jsonify()
	# else:
		# return redirect(url_for('home'))
		
@app.route('/viewpage')
def viewpage():
	if 'username' in session:
		if session['username']=='VinayakaB' or session['username']=='NimeshK':
			clubs=rs.keys('/clubs/*')
			events=rs.keys('/events/*')
			cviews=[]
			eviews=[]
			with db:
				for i in clubs:
					cviews.append([i[7:],rs.hget(i,'views')])
					cur.execute('update clubs set views=views+%s where cid=%s',(rs.hget(i,'views'),i[7:]))
					rs.hset(i,'views',0)
				for i in events:
					eviews.append([i[8:],rs.hget(i,'views')])
					cur.execute('update events set views=views+%s where evid=%s',(rs.hget(i,'views'),i[8:]))
					rs.hset(i,'views',0)
			return render_template('viewpage.html',cviews=cviews,eviews=eviews)
	return redirect(url_for('home'))
	
@app.route('/privacy')
def privacy():
	form1=Signup(request.form)
	form2=Signin(request.form)
	if 'username' in session:
		return render_template('privacy.html',form1=form1,form2=form2,user=session['username'])
	if 'club' in session:
		return render_template('privacy.html',form1=form1,form2=form2,club=session['club'])
	else:
		return render_template('privacy.html',form1=form1,form2=form2)
		
@app.route('/comingsoon')
def fun():
	form1=Signup(request.form)
	form2=Signin(request.form)
	if 'username' in session:
		return render_template('fun.html',form1=form1,form2=form2,user=session['username'])
	if 'club' in session:
		return render_template('fun.html',form1=form1,form2=form2,club=session['club'])
	else:
		return render_template('fun.html',form1=form1,form2=form2)
		
@app.route('/comingsoonqa')
def qasoon():
	form1=Signup(request.form)
	form2=Signin(request.form)
	if 'username' in session:
		return render_template('qa.html',form1=form1,form2=form2,user=session['username'])
	if 'club' in session:
		return render_template('qa.html',form1=form1,form2=form2,club=session['club'])
	else:
		return render_template('qa.html',form1=form1,form2=form2)
	
@app.route('/data')
def data():
	form1=Signup(request.form)
	form2=Signin(request.form)
	if 'username' in session:
		return render_template('data.html',form1=form1,form2=form2,user=session['username'])
	if 'club' in session:
		return render_template('data.html',form1=form1,form2=form2,club=session['club'])
	else:
		return render_template('data.html',form1=form1,form2=form2)	

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return response		
				
if __name__=='__main__':
	app.debug=True
	app.run(host='127.0.0.1')