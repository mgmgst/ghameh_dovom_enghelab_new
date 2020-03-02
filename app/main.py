import config
import MySQLdb
from flask import Flask , render_template,request , redirect,jsonify, flash, url_for, Response, session
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# config
app.config.update(
    SECRET_KEY = config.secret_key
)

limiter = Limiter(
    app,
    key_func=get_remote_address,
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        return "%d" % (self.id)


# create some users with ids 1 to 20       
user = User(0)

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('login')   
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)    

@app.errorhandler(404)
@login_required
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route("/ok")
def sys_check():
    '''this function tell that falsk server is ok and running!!'''
    ret = {'status':'ok','message':'[+] flask server is running'}
    return jsonify(ret) , 200

@app.route('/')
@login_required
def index():    
    return render_template('index.html')

@app.route('/login',methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    '''this function return login page'''
    error = None
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["Password"]
        if check(username,password):
            login_user(user)
            flash('You were successfully logged in','info')
            return redirect(url_for('index'))
        else:
            error = '!!!invalid user!!!' 
               
    return render_template('login.html', error=error)

@app.route('/add',methods=["GET", "POST"])
@login_required
def add():
    if request.method == 'POST':
        name = request.form["name"]
        titlew = request.form["titlew"]
        message = request.form["message"]
        writing_to_database(name,titlew,message)
        return redirect('index')

    else:
        return render_template('add.html')

def check(username,password):
    res = False
    if username == config.usernamein and password == config.passwordin:
        res = True
    return res               

# TODO: make database open for ever for adding works from add page to it when i togel it my self close it

def writing_to_database(name,titlew,message):
    
    db=MySQLdb.connect(host=config.MYSQL_HOST,
                       user=config.MYSQL_USER,
                       passwd=config.MYSQL_PASS,
                       db=config.MYSQL_DB)
    cur = db.cursor()                   
    cur.execute("DROP TABLE IF EXISTS works")
    cur.execute("""CREATE TABLE works (name VARCHAR(100),title VARCHAR(100),message VARCHAR(250));""")
    db.commit()    
    qury = f'INSERT INTO works VALUES ("{name}","{titlew}","{message}");'
    cur.execute(qury)
    db.commit()
    db.close()

# TODO: use it on project and show getted works on main page on table form

def reading_from_database():

    db=MySQLdb.connect(host=config.MYSQL_HOST,
                       user=config.MYSQL_USER,
                       passwd=config.MYSQL_PASS,
                       db=config.MYSQL_DB)
    cur = db.cursor()
    cur.execute("SELECT * FROM works;")
    db.close()
    return dict(cur.fetchall())

if __name__ == "__main__":
    app.run("0.0.0.0",5000,debug=True)
    