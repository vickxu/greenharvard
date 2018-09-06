from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import random

from operator import itemgetter
import json

import helpers
from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///info.db")

@app.route("/")
@login_required
def index():
    """Homepage of index"""
    # get point and dorm info 
    info = db.execute("SELECT * FROM points") 
    
    # initialize a list of tuples to store the points/dorm info (tuple so can sort!)
    tuples_info = []
    for i in range(len(info)):
        tuples_info.append( (info[i]['points'], info[i]['dorm']) )
    # sort (reverse so top score is #1)
    tuples_info.sort(key=itemgetter(0), reverse=True)
    
    # initialize and append to lists for dorm names and points (for display in index)
    dorm_list = []
    dorm_points = []
    for i in range(len(tuples_info)): 
        dorm_list.append(tuples_info[i][1]) 
        dorm_points.append(tuples_info[i][0])
    
    # render template
    return render_template("index.html", dorm_list=dorm_list, dorm_points=dorm_points)
    
@app.route("/about")
def about():
    """About page outlining goals and ideas behind project"""
    return render_template("about.html")

@app.route('/postmethod', methods = ['POST'])
@login_required 
def get_post_javascript_data():
    """Get information from script.js to update SQL tasks table"""
    # retrieve POST call from jscript.js and update tasks
    id = request.form['javascript_data2']
    db.execute("UPDATE tasks SET done = 'true' WHERE id = :id AND user_id=:userid", 
        id=id, userid=session["user_id"])
 
    return id

@app.route('/remove', methods = ['POST'])
@login_required 
def get_post_javascript_data2():
    """Get information from script.js to remove tasks and add points"""
    # retrieve info from script.js and update tasks
    id = request.form['removeid']
    db.execute("UPDATE tasks SET done = 'false' WHERE id = :id AND user_id=:userid", 
        id=id, userid=session["user_id"])
    
    # update points for the user dorm
    dorm = db.execute("SELECT dorm FROM users WHERE id = :id", id=session["user_id"])
    dorm = dorm[0]["dorm"]
    value = db.execute("SELECT * FROM points WHERE dorm = :dorm", dorm= dorm)
    value = value[0]["points"]
    db.execute("UPDATE points SET points = :value WHERE dorm = :dorm", value=value+1, dorm =dorm)
        
    return id

@app.route('/getpythondata')
def get_python_data():
    # get truth values storied in of the tasks for the user 
    rows = db.execute("SELECT done FROM tasks WHERE user_id=:userid",
        userid=session["user_id"])
    
    # make a list 
    truth_vals = [] 
    for i in range(len(rows)):
        truth_vals.append(rows[i]['done'])
    
    # send python>javascript!
    return json.dumps(truth_vals)

@app.route("/myinfo")
@login_required 
def myinfo():
    """Displays graph info about own dorm and yard"""
    # retrieve dorm energy info
    dorminfo = db.execute("SELECT dorm FROM users WHERE id=:id", id=session["user_id"])
    mydorm = dorminfo[0]["dorm"]

    useinfo = db.execute("SELECT * FROM energy2016 WHERE dorm LIKE :dorm", dorm=mydorm)
   
    # get and store piechart values
    electric = [None] * 12
    naturalgas = [None] * 12
        
    for x in range(0, 12):
        word = "use_" + str(x+1)
        electric[x] = int(useinfo[0][word])
        naturalgas[x] = int(useinfo[1][word])
            
    electricsum = sum(electric)/12
    naturalsum = sum(naturalgas)/12
       
    # create variables to send to piechart in helpers 
    name = ["Electric", "Naturalgas", "Steam"]
    values = [electricsum, naturalsum, 0]
    colours = ["rgb(0,255,00)", "rgb(255,0,0)", "rgb(255,255,0)"]
    
    # generate piechart
    piechart = helpers.piechart(name, values, colours)
        
    # store electric energy for dorm for bar chart
    elecarray = [None] * 12
    for x in range(0, 12):
        word = "use_" + str(x+1)
        if x < 8:
            elecarray[x+4] = useinfo[0][word]
        else:
            elecarray[x-8] = useinfo[0][word]

    # generate barchart
    barchart = helpers.barchart(elecarray)
    
    # store electric energy for dorm for table
    elecarray2 = [None] * 13
    for x in range(0, 13):
        if x == 0:
            elecarray2[x] = mydorm
        elif x < 9:
            word = "use_" + str(x)
            elecarray2[x+4] = useinfo[0][word]
        else:
            word = "use_" + str(x)
            elecarray2[x-8] = useinfo[0][word]
                
    # generate table
    table = helpers.table(elecarray2)
    
    # -------------------------------------------------------------- 
    # yard code starts here 
    ivy = ['Apley', 'Hollis', 'Holworthy', 'Lionel', 'Mower', 'Stoughton', 'Straus']
    crimson = ['Greenough','Hurlbut', 'Pennypacker', 'Wigglesworth']
    elm = ['Grays', 'Matthews', 'Weld']
    oak = ['Canaday', 'Thayer']
    
    if mydorm in ivy:
        dorm = ivy
        hyard = "Ivy"
    elif mydorm in crimson: 
        dorm = crimson 
        hyard = "Crimson"
    elif mydorm in elm: 
        dorm = elm 
        hyard = "Elm"
    elif mydorm in oak: 
        dorm = oak 
        hyard = "Oak"

    use = db.execute("SELECT * FROM energy2016 WHERE type = 'Electric (kWh)'")
    
    store = [None] * len(dorm)
    
    # query database for energy information
    for x in range(0, len(dorm)-1):
        useinfo2 = db.execute("SELECT * FROM energy2016 WHERE dorm LIKE :dorm AND type = 'Electric (kWh)'", dorm=dorm[x])
        store[x] = useinfo2[0]["use_7"]
       
    # generate random colours for pie chart 
    colours = [None] * len(dorm)
    
    for i in range(0, len(dorm)-1):
        a = str(random.randrange(256)) + ","
        b = str(random.randrange(256)) + ","
        c = str(random.randrange(256))
        colours[i] = "rgb("+ a + b + c +")"
        
    # generate piechart
    piechart2 = helpers.piechart(dorm, store, colours)

    # render results
    return render_template("myinfo.html", chart=piechart, barchart=barchart, table=table, chart2=piechart2, hyard=hyard, mydorm=mydorm)

# create pie graph for different dorms in a yard
@app.route("/yard", methods=["GET", "POST"])
@login_required
def yard():
    """Search for places that match query."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # dorms of each yard
        ivy = ['Apley', 'Hollis', 'Holworthy', 'Lionel', 'Mower', 'Stoughton', 'Straus']
        crimson = ['Greenough','Hurlbut', 'Pennypacker', 'Wigglesworth']
        elm = ['Grays', 'Matthews', 'Weld']
        oak = ['Canaday', 'Thayer']
        
        dorm = [None] * 8
            
        if request.form.get("yard") == "Ivy":
            dorm = ivy 
        elif request.form.get("yard") == "Crimson":
            dorm = crimson
        elif request.form.get("yard") == "Elm":
            dorm = elm
        elif request.form.get("yard") == "Oak":
            dorm = oak
        
        use = db.execute("SELECT * FROM energy2016 WHERE type = 'Electric (kWh)'")

        store = [None] * len(dorm)
        
        # query database for dorms in yard energy usage
        for x in range(0, len(dorm)):
            useinfo = db.execute("SELECT * FROM energy2016 WHERE dorm LIKE :dorm AND type = 'Electric (kWh)'", dorm=dorm[x])
            store[x] = useinfo[0]["use_7"]

        # generate random colours for pie chart
        colours = [None] * len(dorm)
        for i in range(0, len(dorm)-1):
            a = str(random.randrange(256)) + ","
            b = str(random.randrange(256)) + ","
            c = str(random.randrange(256))
            colours[i] = "rgb("+ a + b + c +")"
            
        # generate piechart
        piechart = helpers.piechart(dorm, store, colours)

        # render results
        return render_template("yarddisplay.html", chart=piechart, hyard=request.form.get("yard"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("yard.html")

# display dorm info --> piegraph of energy type & annual graphs
@app.route("/search", methods=["GET", "POST"])
def search():
    """Search for places that match query."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # query database for username
        useinfo = db.execute("SELECT * FROM energy2016 WHERE dorm LIKE :dorm", dorm=request.form.get("dorm"))
        
        # store electric and gas information and calculate per captia to send to pie chart
        electric = [None] * 12
        naturalgas = [None] * 12
        
        for x in range(0, 12):
            word = "use_" + str(x+1)
            electric[x] = int(useinfo[0][word])
            naturalgas[x] = int(useinfo[1][word])
            
        electricsum = sum(electric)/12
        naturalsum = sum(naturalgas)/12
        
        name = ["Electric", "Naturalgas", "Steam"]
        values = [electricsum, naturalsum, 0]
        colours = ["rgb(0,255,00)", "rgb(255,0,0)", "rgb(255,255,0)"]
    
        # generate piechart
        piechart = helpers.piechart(name, values, colours)
        
        # store energy usage per month to send to bar chart
        elecarray = [None] * 12
        for x in range(0, 12):
            word = "use_" + str(x+1)
            if x < 8:
                elecarray[x+4] = useinfo[0][word]
            else:
                elecarray[x-8] = useinfo[0][word]

        # generate barchart
        barchart = helpers.barchart(elecarray)
        
        # store energy usage per month to send to table
        elecarray2 = [None] * 13
        for x in range(0, 13):
            if x == 0:
                elecarray2[x] = request.form.get("dorm")
            elif x < 9:
                word = "use_" + str(x)
                elecarray2[x+4] = useinfo[0][word]
            else:
                word = "use_" + str(x)
                elecarray2[x-8] = useinfo[0][word]
                
        # generate table
        table = helpers.table(elecarray2)
        

        # render results
        return render_template("display.html", chart=piechart, barchart=barchart, table=table, dorm=request.form.get("dorm"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search.html")

# compare dorm/per capita to country       
@app.route("/search2", methods=["GET", "POST"])
def search2():
    """Search for places that match query."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        error = ""
        
        # ensure country was submitted
        if not request.form.get("country"):
            error += "Please input valid country name"
        
        # error, reload with warning 
        if len(error) > 0:
            return render_template("search2.html", error=error, error_len=len(error))
        
        # no problems 
        else: 
            # query database for dorm information
            dorminfo = db.execute("SELECT * FROM energy2016 WHERE dorm LIKE :dorm", dorm=request.form.get("dorm"))
            
            # query database for username
            countryinfo = db.execute("SELECT * FROM world WHERE country LIKE :country", country=request.form.get("country"))
            
            # generate piechart
            dormarray = [None] * 12
            
            for x in range(0, 12):
                word = "use_" + str(x+1)
                dormarray[x] = int(dorminfo[0][word])
            
            sumdorm = helpers.pc(request.form.get("dorm"),sum(dormarray))
            cinfo = countryinfo[0]["energy_2013"]
    
            # generate comparison barchart
            countrycomp = helpers.countrychart(request.form.get("dorm"), request.form.get("country"), sumdorm, cinfo)
    
            # render results
            return render_template("display2.html", country=countrycomp, hdorm=request.form.get("dorm"), hcountry=request.form.get("country"))
    
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search2.html", error_len=0)

# compare dorm to dorm per capita usage
@app.route("/search3", methods=["GET", "POST"])
def search3():
    """Search for places that match query."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        error = ""
        
        # ensure inputted dorms are different 
        if request.form.get("dorm") == request.form.get("dorm2"):
            error = "Sorry! Please provide 2 different dorms"
            error_len = len(error)
            return render_template("search3.html", error=error, error_len=error_len)
            
        # query database for info on dorm
        useinfo = db.execute("SELECT * FROM energy2016 WHERE dorm LIKE :dorm", dorm=request.form.get("dorm"))
        # query database for info on dorm2
        useinfo2 = db.execute("SELECT * FROM energy2016 WHERE dorm LIKE :dorm", dorm=request.form.get("dorm2"))
        
        elecarray2 = [None] * 13
        
        for x in range(0, 13):
            if x == 0:
                elecarray2[x] = request.form.get("dorm")
            elif x < 6:
                word = "use_" + str(x)
                elecarray2[x+6] = helpers.pc(request.form.get("dorm"),useinfo2[0][word])
            else:
                word = "use_" + str(x)
                elecarray2[x-6] = helpers.pc(request.form.get("dorm"),useinfo2[0][word])
                
        # second dorm into
        elecarray3 = [None] * 12
        
        for x in range(0, 12):
            word = "use_" + str(x+1)
            if x < 6:
                elecarray3[x+6] = helpers.pc(request.form.get("dorm2"),useinfo2[0][word])
            else:
                elecarray3[x-6] = helpers.pc(request.form.get("dorm2"),useinfo2[0][word])

        # generate comparison barchart
        compchart = helpers.comparebar(request.form.get("dorm"), elecarray2, request.form.get("dorm2"), elecarray3)

        # render results
        return render_template("display3.html", compchart=compchart, hdorm=request.form.get("dorm"), hdorm2=request.form.get("dorm2"), error_len=0)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search3.html", error_len=0)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        error = "|" 

        # ensure username was submitted
        if not request.form.get("username"):
            error += " Please input username |"
        # ensure password was submitted
        if not request.form.get("password"):
            error += " Please input password |"
        
        if len(error) > 1:
            return render_template("login.html", error=error, error_len=len(error))

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            error += " Username/password combination incorrect |"
            
        if len(error) > 1:
            return render_template("login.html", error=error, error_len=len(error))

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", error_len=0)

@app.route("/logout")
def logout():
    """Log user out."""
    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # forget any user_id
    session.clear()
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        error = "|"
        
        # ensure text fields submittted 
        if not request.form.get("username"): 
            error += " Must provide username |"
        if not request.form.get("password"):
            error += " Must provide password |"
        if not request.form.get("confirmpassword"):
            error += " Must confirm password |"
        
        # ensure passwords match 
        if not request.form.get("password") == request.form.get("confirmpassword"):
            error += " Passwords do not match |"
        
        # verify username doesn't already exist 
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if len(rows) == 1:
            error += " Username already taken |"
        
        # reload login page with message if some input(s) is/are invalid 
        if len(error) > 1: 
            return render_template("register.html", error=error, error_len=len(error))
            
        # all inputs are valid, store info into database 
        else:      
            # hash the password 
            hash = pwd_context.encrypt(request.form.get("password"))
    
            # put data for new user into database 
            rows = db.execute("INSERT INTO users (id, username, hash, dorm) VALUES(NULL, :username, :hash, :dorm)", 
                    username=request.form.get("username"), 
                    hash = hash, 
                    dorm=request.form.get("dorm"))
            
            # remember which user has logged in
            session["user_id"] = rows
            
            # create tasks (for saving current tasks)
            tasks = ["Turn off lights", "Recycle", "Take shorter shower","Finish all food on plate"]
            for i in range(4):
                db.execute("INSERT INTO tasks (id,task,user_id,done) VALUES(:taskid, :taskname, :userid, 'false')", 
                    taskid=i+1,
                    taskname=tasks[i],
                    userid=session["user_id"])
    
            # redirect user to home page
            flash("You were successfully registered")
            return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", error_len=0)