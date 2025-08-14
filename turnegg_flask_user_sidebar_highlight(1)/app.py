from PIL import Image

from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os


import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max upload size


def allowed_file(filename):
    return '.' in filename and            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)

from flask_socketio import SocketIO, emit, join_room, leave_room

socketio = SocketIO(app)

app.secret_key = 'your_secret_key'
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_first_request
def create_tables():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            bio TEXT, location TEXT, photo TEXT DEFAULT 'default.png'
        )
    ''')
    
    try:
        conn.execute("ALTER TABLE messages ADD COLUMN read INTEGER DEFAULT 0")
        
    conn.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            sender_id INTEGER,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(sender_id) REFERENCES users(id)
        )
    ''')

    
    try:
        conn.execute("ALTER TABLE groups ADD COLUMN avatar TEXT DEFAULT 'default_group.png'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    except sqlite3.OperationalError:
        pass  # already added

    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            sender_id INTEGER,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(sender_id) REFERENCES users(id)
        )
    ''')

    
    try:
        conn.execute("ALTER TABLE groups ADD COLUMN avatar TEXT DEFAULT 'default_group.png'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        file = request.files.get('avatar')
        filename = 'default_group.png'
        if file and '.' in file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                from werkzeug.utils import secure_filename
                import uuid
                filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
                file.save(os.path.join('static/group_icons', filename))
        try:
            conn.execute("INSERT INTO groups (name, created_by, avatar) VALUES (?, ?, ?)", (name, session['user_id'], filename))
            group_id = conn.execute("SELECT id FROM groups WHERE name = ?", (name,)).fetchone()['id']
            conn.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, session['user_id']))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Group name already exists.", "danger")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    except sqlite3.OperationalError:
        pass  # already added

    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            sender_id INTEGER,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(sender_id) REFERENCES users(id)
        )
    ''')

    
    try:
        conn.execute("ALTER TABLE groups ADD COLUMN avatar TEXT DEFAULT 'default_group.png'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already registered.", "danger")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        file = request.files.get('avatar')
        filename = 'default_group.png'
        if file and '.' in file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                from werkzeug.utils import secure_filename
                import uuid
                filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
                file.save(os.path.join('static/group_icons', filename))
        try:
            conn.execute("INSERT INTO groups (name, created_by, avatar) VALUES (?, ?, ?)", (name, session['user_id'], filename))
            group_id = conn.execute("SELECT id FROM groups WHERE name = ?", (name,)).fetchone()['id']
            conn.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, session['user_id']))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Group name already exists.", "danger")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    except sqlite3.OperationalError:
        pass  # already added

    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            sender_id INTEGER,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(sender_id) REFERENCES users(id)
        )
    ''')

    
    try:
        conn.execute("ALTER TABLE groups ADD COLUMN avatar TEXT DEFAULT 'default_group.png'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
        flash("Profile updated.", "success")
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    socketio.run(app, debug=True)


@app.errorhandler(413)
def too_large(e):
    flash("Uploaded file is too large (max 2MB).", "danger")
    return redirect(request.url)



def crop_center_square(image_path):
    try:
        im = Image.open(image_path)
        width, height = im.size
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2
        im_cropped = im.crop((left, top, right, bottom))
        im_cropped.save(image_path)
    except Exception as e:
        print(f"Image crop failed: {e}")



@app.route('/messages/<int:recipient_id>', methods=['GET', 'POST'])
def messages(recipient_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    if request.method == 'POST':
        name = request.form['name']
        file = request.files.get('avatar')
        filename = 'default_group.png'
        if file and '.' in file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                from werkzeug.utils import secure_filename
                import uuid
                filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
                file.save(os.path.join('static/group_icons', filename))
        try:
            conn.execute("INSERT INTO groups (name, created_by, avatar) VALUES (?, ?, ?)", (name, session['user_id'], filename))
            group_id = conn.execute("SELECT id FROM groups WHERE name = ?", (name,)).fetchone()['id']
            conn.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, session['user_id']))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Group name already exists.", "danger")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
        socketio.emit('new_message', {
            'sender_id': session['user_id'],
            'recipient_id': recipient_id,
            'content': content
        }, room=str(recipient_id))
    except sqlite3.OperationalError:
        pass  # already added

    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            sender_id INTEGER,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(sender_id) REFERENCES users(id)
        )
    ''')

    
    try:
        conn.execute("ALTER TABLE groups ADD COLUMN avatar TEXT DEFAULT 'default_group.png'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
        flash("Message sent!", "success")

    user = conn.execute("SELECT * FROM users WHERE id = ?", (recipient_id,)).fetchone()
    chat = conn.execute(
        """
        SELECT * FROM messages
        WHERE (sender_id = ? AND recipient_id = ?)
           OR (sender_id = ? AND recipient_id = ?)
        ORDER BY timestamp ASC
        """, (session['user_id'], recipient_id, recipient_id, session['user_id'])
    ).fetchall()

    conn.execute("UPDATE messages SET read = 1 WHERE recipient_id = ? AND sender_id = ?", (session['user_id'], recipient_id))
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            sender_id INTEGER,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(sender_id) REFERENCES users(id)
        )
    ''')

    
    try:
        conn.execute("ALTER TABLE groups ADD COLUMN avatar TEXT DEFAULT 'default_group.png'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()

    return render_template('messages.html', user=user, chat=chat)







@app.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    user_id = session['user_id']
    inbox_query = conn.execute("""
        SELECT u.id, u.username, u.email, MAX(m.timestamp) AS last_msg,
               SUM(CASE WHEN m.recipient_id = ? AND m.sender_id = u.id AND m.read = 0 THEN 1 ELSE 0 END) AS unread
        FROM users u
        JOIN messages m ON (u.id = m.sender_id AND m.recipient_id = ?)
                        OR (u.id = m.recipient_id AND m.sender_id = ?)
        WHERE u.id != ?
        GROUP BY u.id
        ORDER BY last_msg DESC
    """, (user_id, user_id, user_id, user_id)).fetchall()

    return render_template('inbox.html', contacts=inbox_query)



join_room(str(data['user_id']))
    if 'group_id' in data:
        join_room(f"group-{data['group_id']}")

@socketio.on('leave')
def on_leave(data):
    leave_room(str(data['user_id']))



@app.route('/groups', methods=['GET', 'POST'])
def groups():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    if request.method == 'POST':
        name = request.form['name']
        file = request.files.get('avatar')
        filename = 'default_group.png'
        if file and '.' in file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                from werkzeug.utils import secure_filename
                import uuid
                filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
                file.save(os.path.join('static/group_icons', filename))
        try:
            conn.execute("INSERT INTO groups (name, created_by, avatar) VALUES (?, ?, ?)", (name, session['user_id'], filename))
            group_id = conn.execute("SELECT id FROM groups WHERE name = ?", (name,)).fetchone()['id']
            conn.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, session['user_id']))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Group name already exists.", "danger")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
        except sqlite3.IntegrityError:
            flash("Group name already exists.", "danger")

    all_groups = conn.execute("SELECT g.id, g.name FROM groups g JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = ?", (session['user_id'],)).fetchall()
    return render_template('groups.html', groups=all_groups)

@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
def group_chat(group_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    group = conn.execute("SELECT * FROM groups WHERE id = ?", (group_id,)).fetchone()
    members = conn.execute("SELECT u.username FROM users u JOIN group_members gm ON u.id = gm.user_id WHERE gm.group_id = ?", (group_id,)).fetchall()
    messages = conn.execute("SELECT * FROM group_messages WHERE group_id = ? ORDER BY timestamp ASC", (group_id,)).fetchall()

    return render_template('group_chat.html', group=group, members=members, messages=messages)



@socketio.on('group_message')
def handle_group_message(data):
    group_id = data['group_id']
    sender_id = data['sender_id']
    content = data['content']
    conn = get_db()
    conn.execute("INSERT INTO group_messages (group_id, sender_id, content) VALUES (?, ?, ?)", (group_id, sender_id, content))
    
    try:
        conn.execute("ALTER TABLE groups ADD COLUMN avatar TEXT DEFAULT 'default_group.png'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    emit('group_broadcast', {
        'group_id': group_id,
        'sender_id': sender_id,
        'content': content,
        'is_group': True
    }, to=f"group-{group_id}")


@app.route('/group/<int:group_id>/edit_avatar', methods=['POST'])
def edit_group_avatar(group_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    group = conn.execute("SELECT * FROM groups WHERE id = ?", (group_id,)).fetchone()

    if not group or group['created_by'] != session['user_id']:
        flash("Unauthorized to change this group's avatar.", "danger")
        return redirect(url_for('group_chat', group_id=group_id))

    file = request.files.get('avatar')
    if file and '.' in file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            from werkzeug.utils import secure_filename
            import uuid
            filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
            file.save(os.path.join('static/group_icons', filename))
            conn.execute("UPDATE groups SET avatar = ? WHERE id = ?", (filename, group_id))
            conn.commit()
            flash("Group avatar updated!", "success")

    return redirect(url_for('group_chat', group_id=group_id))
