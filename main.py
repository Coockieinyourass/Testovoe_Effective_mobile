from flask import Flask, render_template, request, session
import sql
from datetime import timedelta

app = Flask(__name__)

app.secret_key = "faodiqfh7m8f9asdn902u3d-0923udp23pdn8v-6avav8m95[yj,c5jioynbq[-mav05'y9cpryjnqmarba]'a6jp34cj5c,w94mvna6[uy]"

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
            sql.cursor.execute("SELECT first_name FROM users WHERE email = ?", (session['user_email'],))
            session['user_first_name'] = sql.cursor.fetchone()[0]
            sql.cursor.execute("SELECT last_name FROM users WHERE email = ?", (session['user_email'],))
            session['user_last_name'] = sql.cursor.fetchone()[0]
            sql.cursor.execute("SELECT fighter FROM users WHERE email = ?", (session['user_email'],))
            session['fighter'] = sql.cursor.fetchone()[0]
            sql.cursor.execute("SELECT admin FROM users WHERE email = ?", (session['user_email'],))
            session['admin'] = sql.cursor.fetchone()[0]
            session.permanent = True
        else:
            print("Пользователь удалён")

    return render_template("login.html")

@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    
    return render_template("profile.html")

@app.route("/delete_account", methods=['POST'])
def delete_account():
    sql.cursor.execute("UPDATE users SET is_active = 0 WHERE email = ?", (session.get('user_email'),))
    sql.conn.commit()
    logout()
    return render_template("register.html")

@app.route("/profile", methods=['POST', 'GET'])
def profile():
    return render_template("profile.html",
                            user=(session['user_first_name'],
                                  session['user_last_name'],
                                  session['user_email'],
                                  session['admin'])
                                if session.get('user_first_name') else None)

def update_user_value(column):
    new_value = request.form.get(column)
    if new_value:
        sql.cursor.execute(
            f"UPDATE users SET {column} = ? WHERE email = ?",
            (new_value, session.get("user_email"))
        )
        if column != "password":
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

@app.route("/rules", methods=['GET'])
def rules():
    if not session.get("user_email"):
        return render_template("error.html", code=(401, "Необходима авторизация")), 401
    
    print(session.get("fighter"))

    if not session.get("fighter") or session.get("fighter") == 0:
        return render_template("error.html", code=(403, "Доступ запрещён")), 403
    
    return render_template("rules.html")

@app.route("/admin_panel", methods=['POST', 'GET'])
def admin_panel():
    sql.cursor.execute("SELECT * FROM users") # Для больших данных надо делать через странички или как угодно, но не всё сразу
    return render_template("admin_panel.html", users=sql.cursor.fetchall())

@app.route("/change_fighter_status", methods=['POST'])
def change_fighter_status():
    if session['admin']:
        fighter = int(request.form.get('fighter'))
        id = request.form.get('user_id')
        
        print(fighter, id)
        sql.cursor.execute("UPDATE users SET fighter = ? WHERE id = ?", (fighter, id))
        sql.conn.commit()

        sql.cursor.execute("SELECT * FROM users")
        return render_template("admin_panel.html", users=sql.cursor.fetchall())
    else:
        return render_template("error.html", code=(403, "Доступ запрещён")), 403

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=False)