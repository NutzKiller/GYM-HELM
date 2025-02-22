from app import db

class DBExercise(db.Model):
    __tablename__ = "exercises"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(10))
    topic = db.Column(db.String(50))
    youtube_video_url = db.Column(db.String(255))  # Full URL to the video
    description = db.Column(db.Text)  # New field for exercise description
    how_to = db.Column(db.Text)       # New field for instructions on how to do it
    trainer_id = db.Column(db.Integer) # the trainer id/ 0=admin

class DBProduct(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)  # formerly 'desc'
    category = db.Column(db.String(50))

class DBUser(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    public_name = db.Column(db.String(100))
    birthday = db.Column(db.String(20))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    profile_photo = db.Column(db.String(200))
    cover_photo = db.Column(db.String(200))
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    weight = db.Column(db.String(20))
    height = db.Column(db.String(20))
    selected_plan = db.Column(db.String(20))
    workout_data = db.Column(db.Text)
    trainer_id = db.Column(db.Integer)
    

    def verify_password(self, password_plaintext):
        # (In a real app, use proper password hashing!)
        return self.password == password_plaintext