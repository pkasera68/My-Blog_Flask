from flask import Flask ,render_template ,url_for
app = Flask(__name__)
post = [
        {
            "author": "Pranav Kasera",
            "title" : "Post1",
            "content" : "this is my first blog post",
            "date_posted" : "May 22, 2020"
        }
    ,
        {
            "author": "Steve braugher",
            "title" : "Post2",
            "content" : "this is my second blog post",
            "date_posted" : "January 22, 2020"
        }
]

title_home="HOME"
title_about="ABOUT"

@app.route("/")
@app.route("/home")
def home():
    return render_template('home_using_layouts.html',post_info=post,title=title_home)


@app.route("/about")
def about():
    return render_template('about_using_layouts.html',title=title_about)

if __name__ == '__main__':
    app.run(debug=True)

