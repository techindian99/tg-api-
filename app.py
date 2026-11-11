import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = sqlite3.connect("file:data.db?mode=ro", uri=True, check_same_thread=False)
    app.state.db.row_factory = sqlite3.Row
    yield
    app.state.db.close()

app = FastAPI(lifespan=lifespan)

PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fast Search</title><style>
body{font-family:system-ui;max-width:700px;margin:30px auto;padding:0 15px;background:#f0f2f5}
input{width:100%;padding:15px;font-size:16px;border:1px solid #ccc;border-radius:8px}
.card{background:#fff;border-radius:8px;padding:15px;margin:10px 0;box-shadow:0 1px 3px rgba(0,0,0,0.1)}
pre{margin:0;white-space:pre-wrap;font-size:14px}
</style></head><body>
<h2>Telegram DB Search</h2>
<input id="q" placeholder="Number (e.g. 79101022111) ya Username (e.g. ashibaev)">
<p id="meta" style="color:#555"></p><div id="out"></div>
<script>
const q=document.getElementById('q'),out=document.getElementById('out'),meta=document.getElementById('meta');
let t;q.oninput=()=>{clearTimeout(t);t=setTimeout(run,300)};
async function run(){
 const v=q.value.trim(); if(!v){out.innerHTML='';meta.textContent='';return}
 meta.textContent='Searching...';
 const r=await fetch('/api/search?q='+encodeURIComponent(v));
 const j=await r.json();
 meta.textContent=j.total+' result mila';
 out.innerHTML=j.items.map(i=>'<div class="card"><pre>'+JSON.stringify(i,null,2)+'</pre></div>').join('');
}
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def home(): return PAGE

@app.get("/api/search")
def search(q: str, limit: int = Query(20, le=50)):
    db = app.state.db
    q = q.strip().lstrip('@')
    query = "SELECT * FROM users WHERE phone = ? OR username = ? OR id = ? LIMIT ?"
    rows = db.execute(query, (q, q, q, limit)).fetchall()
    return {"total": len(rows), "items": [dict(r) for r in rows]}
  
