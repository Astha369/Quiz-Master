from datetime import datetime, timezone
from controllers.database import db

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fullName = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.Integer, nullable=False)
    dOB = db.Column(db.Date, nullable=False)

class Admin(db.Model):
    __tablename__ = "Admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Subject(db.Model):
    __tablename__ = "Subject"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

class Chapter(db.Model):
    __tablename__ = "Chapter"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    subjectId = db.Column(db.Integer, db.ForeignKey('Subject.id'), nullable=False)
    subject = db.relationship('Subject', backref='chapters')
    requiredQualification = db.Column(db.Integer, nullable=False)

class Question(db.Model):
    __tablename__ = "Question"
    id = db.Column(db.Integer, primary_key=True)
    chapterId = db.Column(db.Integer, db.ForeignKey('Chapter.id'), nullable=False)
    quizId = db.Column(db.Integer, db.ForeignKey('Quiz.id'), nullable=False)
    questionText = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    correctOption = db.Column(db.Integer, nullable=False)
    chapter = db.relationship('Chapter', backref='questions')
    quiz = db.relationship('Quiz', backref='questions')

class Quiz(db.Model):
    __tablename__ = "Quiz"
    id = db.Column(db.Integer, primary_key=True)
    chapterId = db.Column(db.Integer, db.ForeignKey('Chapter.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    chapter = db.relationship('Chapter', backref='quizzes')

class Score(db.Model):
    __tablename__ = "Score"
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    quizId = db.Column(db.Integer, db.ForeignKey('Quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref='scores')
    quiz = db.relationship('Quiz', backref='scores')
    takenAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    selectedAnswers = db.Column(db.JSON, nullable=True)
