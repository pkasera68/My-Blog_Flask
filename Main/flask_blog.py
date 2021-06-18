from flask import Flask ,render_template
app = Flask(__name__)
#__name__ is a special variable in python ,which is the name of the module
# ( it represents the __main__ module if we run this script dierectly using python.)


#App routing is used to map the specific URL with the associated function that is intended to perform some task.

#In other words, we can say that if we visit the particular URL mapped to some particular function,
# the output of that function is rendered on the browser's screen.
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return "<h2>About Page</h2>"

# __name__ represents __main__ if run with python and
#this will run script on flask server, if we run it using python.
if __name__ == '__main__':
    app.run(debug=True)