from datetime import datetime
from Main import db,login_manager,app
from flask_login import  UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

#now to make our login system work,
#we have to add the below user_loader ,for the login_manager extension,so that it can get a user by its id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#in User class also inherit the UserMixin class to make the login system work.
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    img_file=db.Column(db.String(20),nullable=False,default='default.jpg')
    password=db.Column(db.String(20),nullable=False)
    #creating 1-to-Many rel. b/w User and Post.
    posts=db.relationship('Post',backref='Author',lazy=True)
    #here
    #1st argument is the name of table with which we are making relationship.
    #2nd arg is backref which means that like a user can access its posts using 'posts' relationship.
    # a post can also get its user info using this backref attr that works in the background.
    #( Basically posts relationship not only access the post but also it adds this backref as hidden attr in the Post
    # table so a post can also access its Author(user).)


    #method to create a secured time sensitive token for 30 min,which will contain the user_id.
    def get_reset_token(self,expires_sec=1800):
        s=Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    #method to verify the token and then return the user of the user_id stored in the token.
    @staticmethod #telling python that it is a static method so do not expect self.
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        #because its imp to first check that whether token has expired its set time or not.
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    #here we need to understand that posts is a Relationship not an attribute
    #so, we would not see it on the schema of the User table, and it will work in the background to give us all
    #the posts written by a User.
    def __repr__(self):
        return f"User('{ self.username }','{ self.email }', '{ self.img_file}')"
#In Python, __repr__ is a special method used to represent a class’s objects as a string.

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    content=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    #here in 'user.id' u of User is small because here its representing the table user
    #not the class User.

    def __repr__(self):
        return f"Post('{ self.title }','{ self.date_posted }')"

#here in the above class we have'nt created an Author attribute because,
#there is a 1-to-Many relationship b/w User and Post and for any Post
#a perticular User would be its Author.
