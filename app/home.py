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

    path = os.path.join(url_for('home.browse'), "data")
    
    path_join = os.path.join

    return render_template('home/browse.html', files=files, path=path, path_join=path_join)

@bp.route('/upload', methods=(['GET', 'POST']))
@login_required
def upload():
    if request.method == 'POST':
        relative_path = request.form['relative_path']
        db = get_db()
        error = None
        
        if 'file' not in request.files or request.files['file'].filename == '':
            error = 'No file uploaded.'

        storage_limit = db.execute(
        'SELECT Value' \
        ' FROM tbl_config' \
        ' WHERE Name = "storage_limit"'
        ).fetchone()

        blob = request.files['file'].read()
        size = len(blob)

        if os.path.getsize(os.path.join(current_app.instance_path, "data")) + size >= int(storage_limit['Value']) * 1000000:
            error = "error/Server out of storage."

        if error == None:
            file = request.files['file']
            filename = secure_filename(file.filename)
            
            Path(os.path.join(current_app.instance_path, "data", relative_path.strip('/').strip('\\'))).mkdir(parents=True, exist_ok=True)

            with open(os.path.join(current_app.instance_path, "data",relative_path, filename), "wb") as binary_file:
                binary_file.write(blob)

            db.execute(
                'INSERT INTO tbl_files ("FileName", "RelativePath", "Timestamp", "UserId")' \
                ' VALUES (?, ?, ?, ?);',
                (filename, relative_path, datetime.now().strftime("%d/%m/%Y %H:%M"), session.get('user_id'))
            )
            db.commit()
            flash("success/File uploaded.")

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

        os.remove(os.path.join(current_app.instance_path, "data" ,file['RelativePath'], file['FileName']))

        try:
            for (root,_,_) in os.walk(os.path.join(current_app.instance_path, "data"), topdown=False):
                os.rmdir(root.replace('\\', '/'))
        except PermissionError:
            pass

        db.execute(
            'DELETE FROM tbl_files'
            ' WHERE Id = ?', (id,)
        )

        db.commit()
        flash("success/File deleted.")
    
    return redirect(url_for('home.index'))

@bp.route('/data/<path:filepath>')
def data(filepath):
    return send_from_directory(os.path.join(current_app.instance_path, "data"), filepath)