import os
from pathlib import Path
from datetime import datetime
from flask import (
    Blueprint, flash, redirect, render_template, request, send_from_directory, session, current_app, url_for
)
from werkzeug.utils import secure_filename

from app.auth import login_required
from app.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/', methods=(['GET']))
@login_required
def browse():
    db = get_db()

    files = db.execute(
        'SELECT' \
        ' F.*' \
        ' ,U.Username' \
        ' FROM tbl_files F' \
        ' JOIN tbl_users U ON U.Id = F.UserId'
    ).fetchall()

    return render_template('home/browse.html', files=files)

@bp.route('/upload', methods=(['GET', 'POST']))
@login_required
def upload():
    if request.method == 'POST':
        relative_path = request.form['relative_path']
        error = None
        
        if 'file' not in request.files or request.files['file'].filename == '':
            error = 'No file uploaded.'

        if error == None:
            file = request.files['file']
            db = get_db()

            filename = secure_filename(file.filename)
            
            Path(os.path.join(current_app.instance_path, "data", relative_path.strip('/').strip('\\'))).mkdir(parents=True, exist_ok=True)

            file.save(os.path.join(current_app.instance_path, "data",relative_path, filename))

            db.execute(
                'INSERT INTO tbl_files ("FileName", "RelativePath", "Timestamp", "UserId")' \
                ' VALUES (?, ?, ?, ?);',
                (filename, relative_path, datetime.now().strftime("%d/%m/%Y %H:%M"), session.get('user_id'))
            )
            db.commit()

        flash(error)

    return render_template('home/upload.html')

@bp.route('/delete')
@bp.route('/delete/<id>', methods=(['POST']))
@login_required
def delete(id):
    if id is not None:
        db = get_db()

        file = db.execute(
        'SELECT *' \
        ' FROM tbl_files' \
        ' WHERE Id = ?', (id,)
        ).fetchone()

        print(file)

        os.remove(os.path.join(current_app.instance_path, "data" ,file['RelativePath'], file['FileName']))

        db.execute(
            'DELETE FROM tbl_files'
            ' WHERE Id = ?', (id,)
        )

        db.commit()
    
    return redirect(url_for('home.index'))

@bp.route('/data/<path:filepath>')
def data(filepath):
    return send_from_directory(os.path.join(current_app.instance_path, "data\\"), filepath)