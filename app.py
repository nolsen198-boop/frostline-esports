import os,sqlite3,json,secrets
from datetime import datetime,timezone
from functools import wraps
from flask import Flask,request,session,redirect,jsonify,render_template_string,abort
from markupsafe import escape
app=Flask(__name__)
app.secret_key=os.getenv('SECRET_KEY',secrets.token_hex(32))
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',SESSION_COOKIE_SECURE=os.getenv('HTTPS','0')=='1',MAX_CONTENT_LENGTH=30000)
DB=os.getenv('DATABASE_PATH',os.path.join(os.path.dirname(__file__),'applications.sqlite3'))
ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD','')
FIELDS=['nickname','age','discord','email','game','platform','experience','rank','tournaments','improve','training','frequency','availability','mic','motivation','teamwork','other']
def conn():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def init():
 with conn() as c:c.execute('CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, nickname TEXT NOT NULL, game TEXT NOT NULL, answers TEXT NOT NULL, paid INTEGER NOT NULL DEFAULT 0, reviewed INTEGER NOT NULL DEFAULT 0)')
init()
@app.get('/')
def home():return open(os.path.join(os.path.dirname(__file__),'index.html'),encoding='utf-8').read()
@app.post('/api/apply')
def apply():
 data=request.get_json(silent=True) or {}
 for k in ['nickname','age','discord','game','platform','experience','improve','training','frequency','availability','mic','motivation','teamwork']:
  if not str(data.get(k,'')).strip():return jsonify(error='Udfyld alle obligatoriske felter.'),400
 if str(data.get('ack','')) not in ['on','true','1']:return jsonify(error='Du skal acceptere betingelserne.'),400
 answers={k:str(data.get(k,''))[:1500] for k in FIELDS}
 with conn() as c:
  cur=c.execute('INSERT INTO applications(created_at,nickname,game,answers) VALUES(?,?,?,?)',(datetime.now(timezone.utc).isoformat(),answers['nickname'],answers['game'],json.dumps(answers,ensure_ascii=False)))
  return jsonify(id=cur.lastrowid),201
def auth(fn):
 @wraps(fn)
 def wrap(*args,**kwargs):
  if not session.get('admin'):return redirect('/admin')
  return fn(*args,**kwargs)
 return wrap
STYLE='''<style>body{font-family:system-ui;background:#071423;color:#eaf6ff;margin:0;padding:35px}a{color:#66d7ff}h1{color:#74dbff}input,button{padding:12px;border-radius:8px;border:1px solid #37536a;background:#132e46;color:white}button{cursor:pointer}article{border:1px solid #254b68;border-radius:12px;padding:20px;margin:14px 0;background:#0e2032}summary{cursor:pointer;font-size:18px;font-weight:bold}dl{display:grid;grid-template-columns:180px 1fr;gap:8px}dt{color:#8fb9d0}dd{margin:0;white-space:pre-wrap;overflow-wrap:anywhere}.tag{color:#91c4de}</style>'''
@app.route('/admin',methods=['GET','POST'])
def admin():
 if request.method=='POST':
  if not ADMIN_PASSWORD:return 'Opsæt ADMIN_PASSWORD på serveren før login.',503
  if secrets.compare_digest(request.form.get('password',''),ADMIN_PASSWORD):session['admin']=True;return redirect('/admin')
  return 'Forkert adgangskode. <a href="/admin">Prøv igen</a>',403
 if not session.get('admin'):return STYLE+'''<h1>Frostline · Ledelsespanel</h1><p>Privat login</p><form method="post"><input name="password" type="password" required placeholder="Adgangskode"><button>Log ind</button></form>'''
 with conn() as c:rows=c.execute('SELECT * FROM applications ORDER BY id DESC').fetchall()
 cards=[]
 for r in rows:
  d=json.loads(r['answers']);details=''.join('<dt>'+str(escape(k))+'</dt><dd>'+str(escape(v))+'</dd>' for k,v in d.items())
  status='Betalt (manuelt bekræftet)' if r['paid'] else 'Ikke bekræftet betalt'
  cards.append(f'''<article><details><summary>#{r['id']} · {escape(r['nickname'])} · {escape(r['game'])} · {status}</summary><p class="tag">Modtaget: {escape(r['created_at'])}</p><dl>{details}</dl><form action="/admin/paid/{r['id']}" method="post"><button>{'Fjern betalingsmarkering' if r['paid'] else 'Markér betaling som kontrolleret'}</button></form><form action="/admin/delete/{r['id']}" method="post" onsubmit="return confirm('Er du sikker på, at du vil slette denne ansøgning permanent?');"><button type="submit" style="background:#7f1d1d;border-color:#ef4444">Slet ansøgning</button></form></details></article>''')
 return STYLE+f'''<h1>Frostline · Ledelsespanel</h1><h2>Ansøgninger: {len(rows)}</h2><p>Betaling bekræftes kun manuelt efter kontrol af MobilePay Box 8620JJ. Første måned er gratis.</p><p><a href="/">Hjemmeside</a> · <a href="/logout">Log ud</a></p>'''+''.join(cards)
@app.post('/admin/paid/<int:rid>')
@auth
def paid(rid):
 with conn() as c:c.execute('UPDATE applications SET paid=CASE WHEN paid=1 THEN 0 ELSE 1 END WHERE id=?',(rid,))
 return redirect('/admin')
@app.get('/logout')
def logout():session.clear();return redirect('/admin')
if __name__=='__main__':
 if not ADMIN_PASSWORD:print('ADVARSEL: Sæt ADMIN_PASSWORD for at kunne logge ind i ledelsespanelet.')
 app.run(host='127.0.0.1',port=5000)
