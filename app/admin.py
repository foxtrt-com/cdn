from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import login_required
from app.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=(['GET']))
@login_required
def index():
    db = get_db()

    config = db.execute(
        'SELECT Name, Value'
        ' FROM tbl_config'
    ).fetchall()

    return render_template('admin/index.html', config=config)

@bp.route('/changepassword', methods=(['POST']))
@login_required
def change_password():
    user_id = session.get('user_id')
    current_password = request.form['current_password']
    password = request.form['password']
    password_confirm = request.form['password_confirm']

    db = get_db()
    error = None
    user = db.execute(
        'SELECT * FROM tbl_users WHERE Id = ?', (user_id,)
    ).fetchone()

    if user['PasswordHash'] == '' and current_password == 'password':
        pass
    elif not check_password_hash(user['password'], current_password):
        error = 'error/Incorrect password.'

    if password != password_confirm:
        error = "error/Passwords dont match."

    if error is None:
        db.execute(
            "UPDATE tbl_users SET PasswordHash = ? WHERE Id = ?",
            (generate_password_hash(password), user_id), 
        )
        db.commit()
        flash("success/Password Updated.")
        return redirect(url_for('admin.index'))

    flash(error)

    return render_template('admin/index.html')

@bp.route('/changeconfig', methods=(['POST']))
@login_required
def change_config():
    storage_limit = request.form['storage_limit']

    db = get_db()

    db.execute(
        "UPDATE tbl_config SET Value = ? WHERE Name = 'storage_limit'",
        (storage_limit,),
    )
    db.commit()

    flash("success/Config Updated.")

    return redirect(url_for('admin.index'))