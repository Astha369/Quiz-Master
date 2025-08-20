from datetime import datetime, timezone
from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request, session
from sqlalchemy import func
from models.model import Subject, User, Chapter, Quiz, Question, Score
from controllers.database import db

student_bp = Blueprint('student', __name__)

@student_bp.route('/studentDashboard')
def studentDashboard():
    if 'user_id' not in session:
        flash("Please log in", "warning")
        return redirect(url_for('auth.studentLogin'))

    user = User.query.get(session['user_id'])
    current_time = datetime.now(timezone.utc)
    qualifiedQuizzes = (
        db.session.query(
            Quiz.id, Quiz.chapterId, Quiz.date, Quiz.duration,
            Chapter.name.label("chapterName"),
            func.count(Question.id).label("questionCount")
        )
        .join(Chapter, Quiz.chapterId == Chapter.id)
        .outerjoin(Question, Question.quizId == Quiz.id)
        .filter(Chapter.requiredQualification == user.qualification)
        .group_by(Quiz.id, Chapter.id)
        .all()
    )

    quizzes_with_timezone = []
    for quiz in qualifiedQuizzes:
        quiz_dict = quiz._asdict()
        quiz_dict["date"] = quiz_dict["date"].replace(tzinfo=timezone.utc)
        quizzes_with_timezone.append(quiz_dict)

    return render_template('student/studentDashboardPage.html', quizzes=quizzes_with_timezone, current_time=current_time)


@student_bp.route('/startQuiz/<int:quizId>')
def startQuiz(quizId):
    quiz = Quiz.query.get_or_404(quizId)
    questions = Question.query.filter_by(quizId=quizId).all()
    
    questions_data = [
        {
            "id": q.id,
            "questionText": q.questionText,
            "option1": q.option1,
            "option2": q.option2,
            "option3": q.option3,
            "option4": q.option4,
            "correctOption": q.correctOption,
        }
        for q in questions
    ]
    return render_template('student/startQuiz.html', quiz=quiz, questions=questions_data)

@student_bp.route('/viewQuizDetails/<int:quizId>')
def viewQuizDetails(quizId):
    quiz = (
        db.session.query(
            Quiz.id, Quiz.chapterId, Quiz.date, Quiz.duration,
            Chapter.name.label("chapterName"),
            Subject.name.label("subjectName"),
            func.count(Question.id).label("questionCount")
        )
        .join(Chapter, Quiz.chapterId == Chapter.id)
        .join(Subject, Chapter.subjectId == Subject.id)
        .outerjoin(Question, Question.quizId == Quiz.id)
        .filter(Quiz.id == quizId)
        .group_by(Quiz.id, Chapter.id, Subject.id)
        .first()
    )

    if not quiz:
        flash("Quiz not found!", "danger")
        return redirect(url_for('student.studentDashboard'))

    return render_template('student/viewQuizDetails.html', quiz=quiz)

@student_bp.route('/submitQuiz/<int:quizId>/<int:score>')
def submitQuiz(quizId, score):
    if 'user_id' not in session:
        flash("Please login", "warning")
        return redirect(url_for('auth.studentLogin'))

    user_id = session['user_id']
    new_score = Score(userId=user_id, quizId=quizId, score=score, takenAt=datetime.now(timezone.utc))
    db.session.add(new_score)
    db.session.commit()

    flash(f"Quiz submitted successfully! Your score: {score}", "success")
    return redirect(url_for('student.studentDashboard'))

@student_bp.route('/quizScores')
def quizScores():
    if 'user_id' not in session:
        flash("Please login", "warning")
        return redirect(url_for('auth.studentLogin'))

    user_id = session['user_id']
    scores = Score.query.filter_by(userId=user_id).join(Quiz).join(Chapter).all()

    return render_template('student/quizScoresPage.html', scores=scores)

@student_bp.route('/summary')
def summary():
    subjectData = (
        db.session.query(Subject.name, func.count(Quiz.id))
        .join(Quiz, Quiz.chapterId == Subject.id)
        .group_by(Subject.name)
        .all()
    )
    subjectData = [{"subject": s[0], "count": s[1]} for s in subjectData]

    monthData = (
        db.session.query(func.strftime('%Y-%m', Score.takenAt), func.count(Score.id))
        .group_by(func.strftime('%Y-%m', Score.takenAt))
        .all()
    )
    monthData = [{"month": m[0], "count": m[1]} for m in monthData]

    return render_template('student/summaryPage.html', subjectData=subjectData, monthData=monthData)

@student_bp.route('/users', methods=['GET'])
def getUsers():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username} for user in users])

@student_bp.route('/users', methods=['POST'])
def addUser():
    data = request.get_json()
    newUser = User(
        username=data['username'],
        password=data['password'],
        fullName=data['fullName'],
        qualification=data['qualification'],
        dOB=data['dOB']
    )
    db.session.add(newUser)
    db.session.commit()
    return jsonify({"message": "User added Successfully"}), 201

@student_bp.route('/subjects', methods=['GET'])
def getSubject():
    subjects = Subject.query.all()
    return jsonify([{"id": subject.id, "name": subject.name, "description": subject.description} for subject in subjects])

@student_bp.route('/chapters', methods=['GET'])
def getChapters():
    chapters = Chapter.query.all()
    return jsonify([{"id": chapter.id, "name": chapter.name, "description": chapter.description, "requiredQualification": chapter.requiredQualification } for chapter in chapters])

@student_bp.route('/quizzes', methods=['GET'])
def getQuiz():
    quizzes = Quiz.query.all()
    return jsonify([{"id": quiz.id, "chapter": quiz.chapter, "date": quiz.date, "duration": quiz.duration} for quiz in quizzes])

@student_bp.route('/quizzes', methods=['POST'])
def addQuizzes():
    data = request.get_json()
    newQuiz = Quiz(
        chapterId=data['chapterId'],
        date=data['date'],
        duration=data['duration']
    )
    db.session.add(newQuiz)
    db.session.commit()
    return jsonify({"message", "Quiz added successfully"}), 201

@student_bp.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.id.ilike(f"%{query}%")).all()
    subject_results = [{"name": s.name} for s in subjects]
    quiz_results = [{"id": q.id, "date": q.date.strftime("%Y-%m-%d")} for q in quizzes]
    return jsonify({"subjects": subject_results, "quizzes": quiz_results})
