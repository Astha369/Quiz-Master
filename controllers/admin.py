from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request, session
from sqlalchemy import func
from models.model import Score, Subject, Chapter, Quiz, Question, User
from controllers.database import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/adminDashboard')
def adminDashboard():
    if 'admin_id' not in session:
        flash("Admin access required!", "danger")
        return redirect(url_for('auth.adminLogin'))
    subjects = Subject.query.all()
    return render_template('admin/adminDashboardPage.html', subjects=subjects)

@admin_bp.route('/addSubject', methods=['GET', 'POST'])
def addSubject():
    if 'admin_id' not in session:
        flash("Admin access required!", "danger")
        return redirect(url_for('auth.adminLogin'))

    if request.method == 'POST':
        subjectName = request.form.get('subjectName')
        subject_description = request.form.get('subjectDescription')

        existingSubject = Subject.query.filter_by(name=subjectName).first()
        if existingSubject:
            flash("Subject already exists!", "warning")
            return redirect(url_for('admin.addSubject'))

        newSubject = Subject(name=subjectName, description=subject_description)
        db.session.add(newSubject)
        db.session.commit()
        flash("Subject added successfully!", "success")
        return redirect(url_for('admin.adminDashboard'))

    return render_template('admin/addSubject.html')

@admin_bp.route('/editSubject/<int:subjectId>', methods=['GET', 'POST'])
def editSubject(subjectId):
    subject = Subject.query.get_or_404(subjectId)

    if request.method == 'POST':
        subject.name = request.form['subjectName']
        subject.description = request.form['subjectDescription']
        db.session.commit()

        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.adminDashboard'))

    return render_template('admin/editSubject.html', subject=subject)

@admin_bp.route('/deleteSubject/<int:subjectId>', methods=['POST'])
def deleteSubject(subjectId):
    subject = Subject.query.get_or_404(subjectId)
    quizzes = Quiz.query.join(Chapter).filter(Chapter.subjectId == subjectId).all()

    for quiz in quizzes:
        Question.query.filter_by(quizId=quiz.id).delete()
        Score.query.filter_by(quizId=quiz.id).delete()
        db.session.delete(quiz)

    Chapter.query.filter_by(subjectId=subjectId).delete()
    db.session.delete(subject)
    db.session.commit()

    flash('Subject and all related data deleted successfully!', 'danger')
    return redirect(url_for('admin.adminDashboard'))

@admin_bp.route('/addChapter/<int:subjectId>', methods=["GET", "POST"])
def addChapter(subjectId):
    subject = Subject.query.get_or_404(subjectId)
    if request.method == 'POST':
        chapterName = request.form.get('chapterName')
        chapterDescription = request.form.get('chapterDescription')
        chapterQualification = request.form.get('chapterQualification')

        newChapter = Chapter(name=chapterName, description=chapterDescription, subjectId=subjectId, requiredQualification=chapterQualification)

        db.session.add(newChapter)
        db.session.commit()
        return redirect(url_for('admin.adminDashboard'))

    return render_template('admin/addChapter.html', subject=subject)

@admin_bp.route('/editChapter/<int:chapterId>', methods=['GET', 'POST'])
def editChapter(chapterId):
    chapter = Chapter.query.get_or_404(chapterId)
    if request.method == 'POST':
        chapter.name = request.form['chapterName']
        chapter.description = request.form['chapterDescription']
        chapter.requiredQualification = request.form.get('chapterQualification')

        db.session.commit()
        return redirect(url_for('admin.adminDashboard'))

    return render_template('admin/editChapter.html', chapter=chapter)

@admin_bp.route('/deleteChapter/<int:chapterId>', methods=['POST'])
def deleteChapter(chapterId):
    chapter = Chapter.query.get_or_404(chapterId)

    quizzes = Quiz.query.filter_by(chapterId=chapterId).all()
    for quiz in quizzes:
        Question.query.filter_by(quizId=quiz.id).delete()
        Score.query.filter_by(quizId=quiz.id).delete()
        db.session.delete(quiz)

    Question.query.filter_by(chapterId=chapterId).delete()
    db.session.delete(chapter)
    db.session.commit()

    flash("Chapter and its quizzes/questions deleted successfully!", "danger")
    return redirect(url_for('admin.adminDashboard'))

@admin_bp.route('/addQuiz', methods=['GET', 'POST'])
def addQuiz():
    if request.method == 'POST':
        chapterId = request.form.get('chapterId')
        quizDate = request.form.get('quizDate')
        duration = request.form.get('duration')

        newQuiz = Quiz(
            chapterId=chapterId,
            date=datetime.strptime(quizDate, '%Y-%m-%d'),
            duration=duration
        )

        db.session.add(newQuiz)
        db.session.commit()
        return redirect(url_for('admin.quizzes'))

    chapters = Chapter.query.all()
    return render_template('admin/addQuiz.html', chapters=chapters)

@admin_bp.route('/editQuiz/<int:quizId>', methods=['GET', 'POST'])
def editQuiz(quizId):
    quiz = Quiz.query.get_or_404(quizId)

    if request.method == 'POST':
        quiz.date = datetime.strptime(request.form['quizDate'], '%Y-%m-%d')
        quiz.duration = request.form['duration']
        db.session.commit()

        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.quizzes'))

    return render_template('admin/editQuiz.html', quiz=quiz)

@admin_bp.route('/deleteQuiz/<int:quizId>', methods=['POST'])
def deleteQuiz(quizId):
    quiz = Quiz.query.get_or_404(quizId)

    Question.query.filter_by(quizId=quizId).delete()
    Score.query.filter_by(quizId=quizId).delete()
    db.session.delete(quiz)
    db.session.commit()

    flash('Quiz and related questions deleted successfully!', 'danger')
    return redirect(url_for('admin.quizzes'))

@admin_bp.route('/addQuestion/<int:quizId>', methods=['GET', 'POST'])
def addQuestion(quizId):
    quiz = Quiz.query.get_or_404(quizId)

    if request.method == 'POST':
        questionText = request.form.get('questionText')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correctOption')

        new_question = Question(
            chapterId=quiz.chapterId,
            quizId=quizId,
            questionText=questionText,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correctOption=correct_option
        )

        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for('admin.quizzes'))

    return render_template('admin/addQuestion.html', quiz=quiz)

@admin_bp.route('/editQuestion/<int:questionId>', methods=['GET', 'POST'])
def editQuestion(questionId):
    question = Question.query.get_or_404(questionId)

    if request.method == 'POST':
        question.questionText = request.form['questionText']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.correctOption = request.form['correctOption']

        db.session.commit()

        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.quizzes'))

    return render_template('admin/editQuestion.html', question=question)

@admin_bp.route('/deleteQuestion/<int:questionId>', methods=['POST'])
def deleteQuestion(questionId):
    question = Question.query.get_or_404(questionId)
    db.session.delete(question)
    db.session.commit()

    flash("Question deleted successfully!", "danger")
    return redirect(url_for('admin.quizzes'))

@admin_bp.route('/quizzes')
def quizzes():
    quiz = Quiz.query.all()
    return render_template('admin/quizPage.html', quizzes=quiz)

@admin_bp.route('/adminSummary')
def adminSummary():
    topScores = (
        db.session.query(Subject.name, func.max(Score.score))
        .join(Chapter, Subject.id == Chapter.subjectId)
        .join(Quiz, Chapter.id == Quiz.chapterId)
        .join(Score, Quiz.id == Score.quizId)
        .group_by(Subject.name)
        .all()
    )
    topScoresData = [{"subject": s[0], "score": s[1]} for s in topScores]

    subjectWiseUsers = (
        db.session.query(Subject.name, func.count(Score.userId.distinct()))
        .join(Chapter, Subject.id == Chapter.subjectId)
        .join(Quiz, Chapter.id == Quiz.chapterId)
        .join(Score, Quiz.id == Score.quizId)
        .group_by(Subject.name)
        .all()
    )
    subjectWiseUsersData = [{"subject": s[0], "users": s[1]} for s in subjectWiseUsers]

    return render_template(
        'admin/adminSummaryPage.html',
        topScoresData=topScoresData,
        subjectWiseUsersData=subjectWiseUsersData
    )

@admin_bp.route('/search', methods=['GET'])
def adminSearch():
    query = request.args.get('q', '').strip().lower()

    if not query:
        return jsonify({"error": "No search query provided"}), 400

    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.id.ilike(f"%{query}%")).all()
    questions = Question.query.filter(Question.questionText.ilike(f"%{query}%")).all()

    results = {
        "users": [{"id": u.id, "username": u.username} for u in users],
        "subjects": [{"id": s.id, "name": s.name} for s in subjects],
        "quizzes": [{"id": q.id, "chapterId": q.chapterId, "date": q.date.strftime('%Y-%m-%d')} for q in quizzes],
        "questions": [{"id": q.id, "text": q.questionText} for q in questions]
    }

    return jsonify(results)
