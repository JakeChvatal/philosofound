# answer.answer_id -> [question.question_id, question.text]
# Accesses the question data associated with an Answer ID
def get_question(db, answerId):
    question = db.execute(
        'SELECT q.question_id, q.text'
        ' FROM question q JOIN answer a on(q.question_id = a.question_id)'
        ' WHERE a.answer_id = ?',
        (answerId,)
    ).fetchone()

# question.question_id -> [answer_id, answer.text, num_respondents]
# retrieves all of the answers to a given question id
# excludes answers that a user has reported
def get_question_answers(db, questionId, userId):
    return db.execute(
        'SELECT a.answer_id, a.text'
        ' FROM answer a JOIN choose c on(a.answer_id = c.answer_id)'
        ' WHERE a.question_id = ?' 
        (questionId,)
    ).fetchall()

# question.question_id -> Number
# counts all of the answers associated with a given question
def count_answers(db, questionId):
    return db.execute(
        'SELECT COUNT(c.user_id) as answer_count'
        ' FROM answer a JOIN choose c on(a.answer_id == c.answer_id)'
        ' WHERE a.question_id == ?'
        ' GROUP BY a.answer_id',
        (questionId,)
    ).fetchone()['answer_count']

# answer.answer_id -> Number
# counts the number of times this answer was chosen
def times_answer_chosen(db, answerId):
    return db.execute(
        'SELECT COUNT(user_id) as count'
        ' FROM choose'
        ' WHERE answer_id = ?',
        (answerId,)
    ).fetchone()['count']

# answer.answer_id, demographic -> [demographic, num_responses, num_chose, percent_chose, answer_selected]
# computes user statistics by demographic information for some answer and chosen demographic
# formatting the string is fine as demographic is limited to a certain enumeration of categories
def get_demographic_info(db, answerId, demographic):
    num_responses = times_answer_chosen(db, answerId)
    if demographic in ["gender", "income", "party", "geography"]:
        return db.execute(
            'SELECT {} as demographic, ? as num_responses, COUNT(c.user_id) as num_chose, ((COUNT(c.user_id) * 100) / ?) as percent_chose, ? as answer_selected'.format(demographic) +
            ' FROM choose c JOIN user u on(c.user_id = u.user_id)'
            ' WHERE answer_id = ?'
            ' GROUP BY gender'
            ' ORDER BY gender',
            (num_responses, num_responses, answerId, answerId)
        ).fetchall()
    else:
        return None

# question.question_id, answer.answer_text -> Boolean
# determines whether a question has a duplicate answer in the database
def has_duplicate_answer(db, questionId, answer_text):
    return db.execute(
        'SELECT *'
        ' FROM answer'
        ' WHERE answer.question_id = ? AND answer.text LIKE ?;',
        (questionId, answer_text,)
    ).fetchone() != None

# answer.answer_id -> Boolean
# determines whether the current user has already voted for an answer
def has_duplicate_vote(db, answer_id, user_id):
    return db.execute(
        'SELECT *'
        ' FROM choose'
        '  WHERE answer_id == ? AND user_id == ?',
        (answer_id, user_id)).fetchall() != None

# question.text -> Boolean
# determines whether a question already exists
def has_duplicate_question(db, question_text):
    return db.execute(
        'SELECT *'
        ' FROM question'
        ' WHERE question.text LIKE ?',
        (question_text,)
    ).fetchone() != None

# question.question_id, user.user_id, answer.answer_text -> answer.answer_id
# creates an answer for a user and votes for that answer
# EFFECT: Creates answer and vote in database
def create_answer(db, question_id, user_id, answer_text):
    # creates the answer
    db.execute(
        'INSERT INTO answer (text, question_id, author_id)'
        ' VALUES (?, ?, ?)',
        (answer_text, question_id, user_id),
    )

    # gets the answer's id
    answer_id = db.execute(
        'SELECT answer.answer_id'
        ' FROM answer'
        ' WHERE answer.text = ? AND answer.question_id = ?',
        (answer_text, question_id)
    ).fetchone()['answer_id']

    # if the user has not already voted for this answer
    if not has_duplicate_vote(db, answer_id, user_id):
        # user automatically chooses an answer they create
        db.execute(
            'INSERT INTO choose (user_id, answer_id)'
            ' VALUES (?, ?)',
            (user_id, answer_id)
        )

    return answer_id

# question.text, user.user_id -> question.question_id
# creates a question and returns its id
# EFFECT: creates a question in the question database
def create_question(db, question_text, user_id):
    # creates a question
    db.execute(
        'INSERT INTO question (text, author_id)'
        ' VALUES (?, ?)',
        (question_text, user_id),
    )

    # gets the id of the just-generated question
    return db.execute(
        'SELECT question.question_id as question_id'
        ' FROM question'
        ' WHERE question.text = ?',
        (question_text,)
    ).fetchone()['question_id']
