from flask import Flask, render_template, request, redirect, escape, session
from vsearch import search4letters
from DBcm import UseDatabase
from checker import check_logged_in
from threading import Thread


app = Flask(__name__)
app.secret_key = 'PitterParker'

if __name__ == '__main__':
    app.config['dbconfig'] = { 'host': '127.0.0.1',
                                'user': 'Roman',
                                'password': 'Drtf11',
                                'database': 'vsearchlogDB', }
else:
    app.config['dbconfig'] = {  'host': 'baltazar164.mysql.pythonanywhere-services.com',
                                'user': 'baltazar164',
                                'database': 'baltazar164$vsearchlogdb',
                                'password': '8.dr4G$?F!szb6g'}

@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return "«You are now logged in"

@app.route('/logout')
def do_logout() ->str:
    del session['logged_in']
    return 'You are now logged out'


@app.route('/status')
def check_status() -> str:
    if 'logged_in' in session:
        return "«You are currently logged in"
    else:
        return "«You are NOT logged in»"


def write_error(info, p = 'w'):
    with open('error_info.txt', p) as error_file:
        print(info, file=error_file)


def log_request(req: 'flask_request', res: str) -> None:
    '''write information about request into MySQL database "vsearchlogdb"'''
    
    dbconfig = app.config['dbconfig']
    _SQL = '''insert into log
            (phrase, letters, ip, browser_string, results)
            values
            (%s, %s, %s, %s, %s)'''

    try:
        with UseDatabase(dbconfig) as cursor:
            arguments = (req.form['phrase'], req.form['letters'], req.remote_addr, str(req.user_agent), res)
            cursor.execute(_SQL, arguments)
    except Exception as err:
        print('**** Loggin failed with this error:', str(err))    


@app.route('/viewlog')
@check_logged_in
def viewlog() -> 'vsearchlogdb':

    _SQL = '''SELECT
        phrase,
        letters,
        ip,
        browser_string,
        results
    from log'''


    with UseDatabase(app.config['dbconfig']) as cursor:
        cursor.execute(_SQL)
        data = cursor.fetchall()

    titles = ('phrase', 'letters', 'ip', 'browser_string', 'results')
    return render_template('viewlog.html',
                           the_titile = 'View Log',
                           the_row_titles = titles,
                           the_data = data,)


@app.route('/search4', methods = ['POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your result:'
    results = str(search4letters(phrase, letters))

    t_log_request = Thread(target = log_request, args = (request, results))
    t_log_request.start()
    
    return render_template('results.html',
                           the_titile=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results)


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title = 'Welcome to seatch4letters on the web!')

if __name__ == '__main__':
    app.run(debug = True)