from run import *

def present(a):
	def _present(form, field):
		sql='select '+a+' from login where '+a+' =%s'
		with db:	
			cur.execute(sql,(field.data,))
			ld=cur.fetchall()
			if ld:
				raise validators.ValidationError(a+' already used')
	return _present
	
def fpresent(a):
	def _fpresent(form, field):
		sql='select '+a+' from fac where '+a+' =%s'
		with db:
			cur.execute(sql, (field.data,))
			ld=cur.fetchall()
			if ld:
				raise validators.ValidationError(a+' already used')
	return _fpresent 			
	
def absent(a,message="Error"):
	def _absent(form, field):
		sql='select '+a+' from login where '+a+' =%s'
		with db:
			cur.execute(sql,(field.data,))
			ld=cur.fetchall()
			if ld:
				pass
			else:	
				raise validators.ValidationError(message)
	return _absent
	
def absentp(a,message="Error"):
	def _absentp(form, field):
		sql='select username,pass from login where email=%s'
		with db:
			cur.execute(sql,(form.email.data,))
			ld=cur.fetchall()
			if ld:
				fd=ld[0][0]+field.data
				fdp=hashlib.md5()
				fdp.update(fd)
				fd=fdp.hexdigest()
				if ld[0][1]==fd:
					pass
				else:		
					raise validators.ValidationError(message)	
			else:	
				raise validators.ValidationError(message)
	return _absentp	
    
with db:
	cur.execute('select * from colleges order by cname');
	collegelist=list(cur.fetchall())
	collegelist.insert(0,('0','Select College'))
	
class Signup(Form):
	username = TextField('Username', [
		validators.Required("Username can not be empty"),
		validators.Length(min=4, max=16, message="Username length should be between 4 to 16 characters"),
		validators.Regexp('[a-zA-Z0-9.]',message="Username can contain only Letters Numbers and Periods"),
		present('Username')
		],)
	reg=TextField('Registration No.', [
		validators.Required("Registration No can not be empty"),
		validators.Length(min=8, max=9, message="Error"),
		present('Reg'),
		],)
	email=EmailField('Email', [
		validators.Required("Email can not be empty"),
		validators.Length(min=8, max=50, message=None),
		present('Email')
	],)
	college = SelectField('College',choices=collegelist,coerce=int)
	    
class Signin(Form):  
	email = EmailField('', [
		validators.Length(min=8, max=50, message='Invalid Email-ID or Password'),
		absent('Email', message='Invalid Email-ID or Password')
		],)
	password = PasswordField('', [
		validators.Required(message="Invalid Email-ID or Password"),
		absentp('Pass',message="Invalid Email-ID or Password")
		],)
	
class passchange(Form):
	password = PasswordField('Password', [validators.Required(),validators.Length(min=6, max=20, message=None),validators.EqualTo('repass', message='Passwords must match')],)
	repass=PasswordField('ReEnter Password', [validators.Required()])
	
class fpassw(Form):
	email=EmailField('Email', [
		absent('Email',message="Err")
		],)

class faculty(Form):
	id = TextField('', [
		validators.Required(message='Error'),
		validators.Length(min=6, max=9, message='Error'),
		fpresent('id')
		],)
	fname = TextField('', [
		validators.Required(message='Error'),
		validators.Length(min=4, max=36, message='Error')
		],)
	fdept = TextField('', [
		validators.Required(message='Error'),
		validators.Length(min=4, max=50, message='Error')
		],)

class facrev(Form):
	id = TextField('', [
		validators.Required(message='Error'),
		validators.Length(min=6, max=9, message='Error')
		],)
	username = TextField('', [
		validators.Required(message='Error'),
		validators.Length(min=4, max=16, message="Invalid Username or Password")
		],)
	rat1 = TextField('', [
		validators.Required(message='Error'),
		],)
	rat2 = TextField('', [
		validators.Required(message='Error'),
		],)
	rat3 = TextField('', [
		validators.Required(message='Error'),
		],)
	rat4 = TextField('', [
		validators.Required(message='Error'),
		],)
	srat1 = TextField('', [
		validators.Required(message='Error'),
		],)
	srat2 = TextField('', [
		validators.Required(message='Error'),
		],)
	rev = TextField('', [
		validators.Required(message='Error'),
		validators.Length(min=0, max=250, message='Error')
		],)
	srev = TextField('', [
		validators.Required(message='Error'),
		validators.Length(min=0, max=250, message='Error')
		],)	