from flask import Flask, render_template, request, session
import sql
from datetime import timedelta

app = Flask(__name__)

app.secret_key = 'Секретный ключ для работы сессии и хранения данных в куки'

app.permanent_session_lifetime = timedelta(days=365)

@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("index.html")


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        print(request.form)
        print(request.form.get("first_name"))

        sql.registration(request.form.get("first_name"),
                         request.form.get("last_name"),
                         request.form.get("email"),
                         request.form.get("password"),
                         request.form.get("confirm_password"))
        
        # session['user_first_name'] = request.form.get("first_name")
        # session['user_last_name'] = request.form.get("last_name")
        # session['user_email'] = request.form.get("email")
        # session['user_password'] = request.form.get("password")
        # session.permanent = True
        
    return render_template("register.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        print(request.form)

        sql.login(email,
                request.form.get("password"))
        
        sql.cursor.execute("SELECT is_active FROM users WHERE email = ?", (email,))
        is_active = sql.cursor.fetchone()
        if is_active:
            session['user_email'] = email # Добавил здесь, потому что по тестовому надо запоминать пользователя после логина
            session['user_password'] = request.form.get("password")
            sql.cursor.execute("SELECT first_name FROM users WHERE email = ?", (session['user_email'],))
            session['user_first_name'] = sql.cursor.fetchone()[0]
            sql.cursor.execute("SELECT last_name FROM users WHERE email = ?", (session['user_email'],))
            session['user_last_name'] = sql.cursor.fetchone()[0]
            session.permanent = True
        else:
            print("Пользователь удалён")

    return render_template("login.html")

@app.route("/logout", methods=['POST'])
def logout():
    session['user_first_name'] = None
    session['user_last_name'] = None
    session['user_email'] = None
    session['user_password'] = None
    
    return render_template("profile.html")

@app.route("/delete_account", methods=['POST'])
def delete_account():
    sql.cursor.execute("UPDATE users SET is_active = 0 WHERE email = ?", (session.get('user_email'),))
    sql.conn.commit()
    logout()
    return render_template("register.html")

@app.route("/profile", methods=['POST', 'GET'])
def profile():
    return render_template("profile.html", user=(session['user_first_name'], session['user_last_name'], session['user_email']) if session.get('user_first_name') else None)

def update_user_value(column):
    new_value = request.form.get(column)
    if new_value:
        sql.cursor.execute(
            f"UPDATE users SET {column} = ? WHERE email = ?",
            (new_value, session.get("user_email"))
        )
        session[f"user_{column}"] = new_value
        sql.conn.commit()

@app.route("/update_profile", methods=['POST'])
def update_profile():
    update_user_value("first_name")
    update_user_value("last_name")
    if request.form.get("email"):
        sql.cursor.execute("SELECT email FROM users WHERE email = ?", (request.form.get("email"),))
        old_email = sql.cursor.fetchone()
        if old_email == None:
            update_user_value("email")
        else:
            print("Такая почта уже используется")
    update_user_value("password")

    return render_template("profile.html", user=(session['user_first_name'], session['user_last_name'], session['user_email']) if session.get('user_first_name') else None)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=False)