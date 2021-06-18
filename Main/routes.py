import secrets,os
from flask import render_template ,url_for ,flash ,redirect,request,abort
from PIL import Image
#defining import modles after db to avoid circular imports.
from Main import app,db,bcrypt,mail
from Main.models import User,Post
from Main.forms import (RegisterForm, LoginForm ,AccountUpdateForm ,PostForm
                        ,RequestResetForm,ResetPasswordForm)
from flask_login import login_user, current_user,logout_user,login_required
from flask_mail import Message
title_home="HOME"
title_about="ABOUT"
@app.route("/")
@app.route("/home")
def home():
    #getting all posts
    #showing all the posts on a single page is not a good idea, so lets paginate all the posts.
    #we will use query.paginate() method of sqlalchemy that will return a pagination object
    #this object will represent the whole pagination and
    #at a time will point to a single page that will contain items that belong to that
    #perticular page after pagination.
    #to see all methods of this paginate lib use dir(paginate_obj) in py interpr.

    page=request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=3)
    return render_template('home_using_layouts.html',post_info=posts,title=title_home)


@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
            return redirect(url_for('home'))

    form_obj= RegisterForm()
    if form_obj.validate_on_submit():#validate_on_submit() checks that if the form is
                                     # validated correctly after submission.
        hashed_pss = bcrypt.generate_password_hash(form_obj.password.data).decode('utf-8')
        user=User(username=form_obj.username.data,email=form_obj.email.data,password=hashed_pss)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created !','success')
        return redirect(url_for('login'))

    return render_template("Register.html",title="Sign Up",form=form_obj)


@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
            return redirect(url_for('home'))

    form_obj= LoginForm()
    if form_obj.validate_on_submit():
        user=User.query.filter_by(username=form_obj.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form_obj.password.data):
            login_user(user,remember=form_obj.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Unsuccessfull Login! Please check username and password.', 'danger')
    return render_template("Login.html",title="Login",form=form_obj)

@app.route("/about")
def about():
    return render_template('about_using_layouts.html',title=title_about)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

#function for saving the picture in the static/profile pics.
def save_picture(form_picture):
    #we will save picture by a random secret key.
    sec_name= secrets.token_hex(8)
    _,file_ext=os.path.splitext(form_picture.filename)
    picture_fn=sec_name+file_ext
    #getting path to save it.
    picture_path=os.path.join(app.root_path,'static/profile pics',picture_fn)
    #Now,any picture(small or large) in size you upload
    #css shows it in 125 X 125 so since large images will take
    #alot of size to store and also makes our website slow we will resize them to 125 X 125 by ourselves.
    new_dim=(125,125)
    i = Image.open(form_picture)
    i.thumbnail(new_dim)

    i.save(picture_path)
    return picture_fn

@app.route("/account",methods=['GET','POST'])
@login_required #placing login_required decorator , so that user can only access its account if he is login.
def account():
    form_obj=AccountUpdateForm()
    if form_obj.validate_on_submit():
        if form_obj.picture.data:
            #saving the picture in the static/profile picture folder.
                picture_file=save_picture(form_obj.picture.data)
                current_user.img_file=picture_file

        current_user.username=form_obj.username.data
        current_user.email=form_obj.email.data

        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':#by this condition user will get its current username and password
        form_obj.username.data = current_user.username# already filled in the fileds
        form_obj.email.data=current_user.email

    userimage= url_for('static',filename="profile pics/" + current_user.img_file)
    return render_template('account.html', title='My Profile'
                           ,userimage=userimage,form=form_obj)

@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    form_obj=PostForm()
    if form_obj.validate_on_submit():
        #creting the post in the database.
        post= Post(title=form_obj.title.data,content=form_obj.content.data,Author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='Create Post',form=form_obj,legend="New Post")

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update",methods=['POST','GET'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.Author != current_user:
        abort(403)
    form_obj=PostForm()
    if form_obj.validate_on_submit():
        post.title=form_obj.title.data
        post.content=form_obj.content.data
        db.session.commit()
        flash('Your post has been updated!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':
        form_obj.title.data=post.title
        form_obj.content.data=post.content
    return render_template('create_post.html', title='Update Post', form=form_obj,legend="Update Post")

@app.route("/post/<int:post_id>/delete",methods=['POST','GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.Author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted successfully!','success')
    return redirect(url_for('home'))

#this route is for filtering the posts by a specific user's username.
@app.route("/user/<string:username>")
def user_posts(username):
    page=request.args.get('page',1,type=int)
    user=User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(Author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=3)

    title=username+"'s Posts"
    return render_template('user_posts.html',post_info=posts,title=title, user=user)

def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message("Password Reset Request",sender='noreply@demo.com',recipients=[user.email])


    msg.body=f'''To reset your password, visit the following Link:
    {url_for('reset_password',token=token,_external=True)}
    
    if you have not made this request then simply ignore this message.
    '''
    #setting the _external=True to get a absolute url(complete url), not a relative in the mail.
    mail.send(msg)


@app.route("/reset_password",methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
            return redirect(url_for('home'))
    form_obj=RequestResetForm()
    if form_obj.validate_on_submit():
        user=User.query.filter_by(email=form_obj.email.data).first()
        send_reset_email(user)
        flash("An email has been sent to the registered email, with instructions to reset password.",'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title="Reset Password",form=form_obj)

@app.route("/reset_password/<token>",methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
            return redirect(url_for('home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash('The token is invalid or has expired','warning')
        return redirect(url_for('reset_request'))
    form_obj=ResetPasswordForm()
    if form_obj.validate_on_submit():
        hashed_pss = bcrypt.generate_password_hash(form_obj.password.data).decode('utf-8')
        user.password = hashed_pss
        db.session.commit()
        flash(f'Your password has been updated!','success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title="Reset Password", form=form_obj)
