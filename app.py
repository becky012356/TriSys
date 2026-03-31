import streamlit as st
import pymssql

st.set_page_config(page_title="TriSys", page_icon="📊", layout="centered")

# ── DB ───────────────────────────────────────────────────────────────────────

def get_conn():
    cfg = st.secrets["db"]
    return pymssql.connect(
        server=cfg["server"], port=int(cfg["port"]),
        user=cfg["user"], password=cfg["password"], database=cfg["database"]
    )

def query(sql, params=None):
    conn = get_conn()
    cur = conn.cursor(as_dict=True)
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    conn.close()
    return rows

def execute(sql, params=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    conn.close()

# ── Session state ────────────────────────────────────────────────────────────

for k, v in [("user", None), ("page", "main"), ("edit", None), ("adding", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Global CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* Hide Streamlit default chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 520px; }

/* ── Login ── */
.login-wrap {
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
    padding: 24px;
}
.login-card {
    background: #fff;
    border-radius: 20px;
    padding: 40px 32px;
    width: 100%; max-width: 380px;
    box-shadow: 0 16px 48px rgba(0,0,0,.22);
}
.login-title {
    text-align: center;
    font-size: 28px; font-weight: 700;
    color: #1a73e8; margin-bottom: 8px;
}
.login-sub {
    text-align: center; color: #888;
    font-size: 14px; margin-bottom: 28px;
}

/* ── Page header ── */
.page-header {
    background: linear-gradient(135deg, #1a73e8, #0d47a1);
    color: #fff; padding: 18px 20px 14px;
    display: flex; align-items: center; justify-content: space-between;
}
.page-header h2 { margin: 0; font-size: 20px; }

/* ── Main menu ── */
.welcome-bar {
    background: linear-gradient(135deg, #1a73e8, #0d47a1);
    color: #fff; padding: 24px 20px 20px;
    margin-bottom: 4px;
}
.welcome-bar h2 { margin: 0 0 4px; font-size: 22px; }
.welcome-bar p  { margin: 0; font-size: 14px; opacity: .85; }

.menu-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; padding: 16px; }
.menu-card {
    border-radius: 18px; padding: 28px 16px;
    text-align: center; cursor: pointer;
    box-shadow: 0 4px 14px rgba(0,0,0,.12);
    transition: transform .12s, box-shadow .12s;
    border: none; width: 100%; color: #fff;
    font-size: 17px; font-weight: 700;
}
.menu-card:hover  { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(0,0,0,.18); }
.menu-card:active { transform: scale(.97); }
.menu-card .icon  { font-size: 42px; display: block; margin-bottom: 10px; }
.mc-cust { background: linear-gradient(135deg, #43a047, #2e7d32); }
.mc-fact { background: linear-gradient(135deg, #1e88e5, #1565c0); }
.mc-item { background: linear-gradient(135deg, #fb8c00, #e65100); }
.mc-user { background: linear-gradient(135deg, #8e24aa, #6a1b9a); }

/* ── CRUD page ── */
.crud-header {
    background: linear-gradient(135deg, #1a73e8, #0d47a1);
    color: #fff; padding: 16px 20px;
    font-size: 20px; font-weight: 700;
    margin-bottom: 0;
}
.search-row { padding: 12px 16px 0; display: flex; gap: 8px; }
.toolbar-row { padding: 8px 16px 12px; }

/* Table */
.tbl { width: 100%; border-collapse: collapse; font-size: 14px; }
.tbl th {
    background: #1a73e8; color: #fff;
    padding: 10px 10px; text-align: left; font-weight: 600;
}
.tbl td { padding: 9px 10px; border-bottom: 1px solid #eef0f3; vertical-align: middle; }
.tbl tr:nth-child(even) td { background: #f7f9fc; }
.tbl tr:hover td { background: #e8f0fe; }

/* Badges for action buttons */
.badge-edit {
    background:#fff3e0; color:#e65100; border:1px solid #ffcc80;
    border-radius:6px; padding:3px 10px; font-size:13px; cursor:pointer;
    margin-right:4px;
}
.badge-del {
    background:#fce4ec; color:#c62828; border:1px solid #ef9a9a;
    border-radius:6px; padding:3px 10px; font-size:13px; cursor:pointer;
}

/* Form card */
.form-card {
    background: #fff;
    border: 1px solid #e0e7ff;
    border-left: 4px solid #1a73e8;
    border-radius: 12px;
    padding: 20px 18px 10px;
    margin: 0 16px 16px;
    box-shadow: 0 2px 8px rgba(26,115,232,.08);
}
.form-card h4 { margin: 0 0 16px; color: #1a73e8; font-size: 16px; }

/* Streamlit form overrides */
div[data-testid="stForm"] { border: none !important; padding: 0 !important; }
div[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1px solid #dde2eb !important;
    padding: 10px 14px !important;
    font-size: 15px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #1a73e8 !important;
    box-shadow: 0 0 0 2px rgba(26,115,232,.15) !important;
}
div[data-testid="stSelectbox"] > div { border-radius: 8px !important; }

/* Primary button */
div[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"],
div[data-testid="stFormSubmitButton"] button {
    background: #1a73e8 !important; color: #fff !important;
    border-radius: 8px !important; font-size: 15px !important;
    border: none !important;
}

/* Notification */
div[data-testid="stToast"] { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Login ────────────────────────────────────────────────────────────────────

def login_page():
    st.markdown('<div class="login-wrap"><div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">📊 TriSys</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">企業資料管理系統</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        userid = st.text_input("用戶代碼", placeholder="請輸入帳號")
        pwd    = st.text_input("密碼", type="password", placeholder="請輸入密碼")
        ok     = st.form_submit_button("🔐  登　入", use_container_width=True)

    if ok:
        rows = query("SELECT userid, username FROM [user] WHERE userid=%s AND pwd=%s", (userid, pwd))
        if rows:
            st.session_state.user = rows[0]
            st.rerun()
        else:
            st.error("帳號或密碼錯誤，請重新輸入")

    st.markdown('</div></div>', unsafe_allow_html=True)

# ── Main menu ────────────────────────────────────────────────────────────────

def main_page():
    u = st.session_state.user
    st.markdown(f"""
    <div class="welcome-bar">
      <h2>👋 歡迎回來，{u['username']}</h2>
      <p>請選擇要操作的功能</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👥\n\n客戶資料", use_container_width=True, key="btn_cust"):
            st.session_state.page = "cust"; st.rerun()
        if st.button("📦\n\n商品資料", use_container_width=True, key="btn_item"):
            st.session_state.page = "item"; st.rerun()
    with col2:
        if st.button("🏭\n\n廠商資料", use_container_width=True, key="btn_fact"):
            st.session_state.page = "fact"; st.rerun()
        if st.button("🔑\n\n用戶管理", use_container_width=True, key="btn_user"):
            st.session_state.page = "user"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("登出", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# ── CRUD helpers ─────────────────────────────────────────────────────────────

def back_btn(title, icon=""):
    col1, col2 = st.columns([1, 6])
    if col1.button("←"):
        st.session_state.page = "main"
        st.session_state.edit = None
        st.session_state.adding = False
        st.rerun()
    st.markdown(f'<div class="crud-header">{icon} {title}</div>', unsafe_allow_html=True)

def show_form(title, fields, defaults, on_save, disabled_keys=None):
    st.markdown(f'<div class="form-card"><h4>✏️ {title}</h4>', unsafe_allow_html=True)
    vals = {}
    with st.form("crud_form"):
        for key, label, ftype, *extra in fields:
            default = defaults.get(key, "") or ""
            dis = bool(disabled_keys and key in disabled_keys)
            if ftype == "select":
                options = extra[0] if extra else []
                labels  = extra[1] if len(extra) > 1 else options
                idx = options.index(default) if default in options else 0
                vals[key] = st.selectbox(label, options, index=idx,
                                         format_func=lambda x, o=options, l=labels: l[o.index(x)],
                                         disabled=dis)
            else:
                vals[key] = st.text_input(label, value=default, disabled=dis)
        c1, c2 = st.columns(2)
        saved  = c1.form_submit_button("💾 儲存", use_container_width=True)
        cancel = c2.form_submit_button("取消",    use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if saved:
        on_save(vals)
    if cancel:
        st.session_state.edit = None
        st.session_state.adding = False
        st.rerun()

def render_table(rows, col_keys, col_headers, key_prefix, on_edit, on_del):
    if not rows:
        st.info("查無資料")
        return
    header_html = "".join(f"<th>{h}</th>" for h in col_headers) + "<th style='width:90px'>操作</th>"
    rows_html = ""
    for row in rows:
        cells = "".join(f"<td>{row.get(k,'')}</td>" for k in col_keys)
        pk = row[col_keys[0]]
        rows_html += f"""<tr>{cells}
          <td>
            <span class='badge-edit' id='edit_{key_prefix}_{pk}'>修改</span>
            <span class='badge-del'  id='del_{key_prefix}_{pk}'>刪除</span>
          </td></tr>"""
    st.markdown(f"""
    <div style="padding:0 16px 16px">
      <table class='tbl'><thead><tr>{header_html}</tr></thead>
      <tbody>{rows_html}</tbody></table>
    </div>""", unsafe_allow_html=True)

    # Streamlit buttons (hidden but functional) placed in a tight row per record
    for row in rows:
        pk = row[col_keys[0]]
        c1, c2, *_ = st.columns([1, 1, 8])
        if c1.button("✏", key=f"e_{key_prefix}_{pk}", help="修改"):
            on_edit(row)
        if c2.button("🗑", key=f"d_{key_prefix}_{pk}", help="刪除"):
            on_del(pk)

# ── CUST ─────────────────────────────────────────────────────────────────────

def cust_page():
    back_btn("客戶資料維護", "👥")
    fields = [("cust_code","客戶代碼","text"), ("cust_name","客戶名稱","text"), ("remark","備註","text")]

    col1, col2 = st.columns([4, 1])
    q = col1.text_input("", placeholder="🔍 搜尋代碼 / 名稱", label_visibility="collapsed", key="cust_q")
    if col2.button("＋ 新增", key="cust_add", use_container_width=True):
        st.session_state.adding = True; st.session_state.edit = None

    sql = "SELECT * FROM cust" + (" WHERE cust_code LIKE %s OR cust_name LIKE %s" if q else "") + " ORDER BY cust_code"
    rows = query(sql, (f"%{q}%", f"%{q}%") if q else None)

    if st.session_state.adding:
        def do_add(v):
            try:
                execute("INSERT INTO cust VALUES (%s,%s,%s)", (v["cust_code"], v["cust_name"], v["remark"]))
                st.session_state.adding = False; st.toast("新增成功 ✅"); st.rerun()
            except Exception as e: st.error(str(e))
        show_form("新增客戶", fields, {}, do_add)

    elif st.session_state.edit:
        def do_edit(v):
            execute("UPDATE cust SET cust_name=%s, remark=%s WHERE cust_code=%s",
                    (v["cust_name"], v["remark"], v["cust_code"]))
            st.session_state.edit = None; st.toast("修改成功 ✅"); st.rerun()
        show_form("修改客戶", fields, st.session_state.edit, do_edit, disabled_keys=["cust_code"])

    def on_edit(row): st.session_state.edit = dict(row); st.session_state.adding = False; st.rerun()
    def on_del(pk):
        execute("DELETE FROM cust WHERE cust_code=%s", (pk,)); st.toast("已刪除"); st.rerun()
    render_table(rows, ["cust_code","cust_name","remark"], ["客戶代碼","客戶名稱","備註"], "c", on_edit, on_del)

# ── FACT ─────────────────────────────────────────────────────────────────────

def fact_page():
    back_btn("廠商資料維護", "🏭")
    fields = [("fact_code","廠商代碼","text"), ("fact_name","廠商名稱","text"), ("remark","備註","text")]

    col1, col2 = st.columns([4, 1])
    q = col1.text_input("", placeholder="🔍 搜尋代碼 / 名稱", label_visibility="collapsed", key="fact_q")
    if col2.button("＋ 新增", key="fact_add", use_container_width=True):
        st.session_state.adding = True; st.session_state.edit = None

    sql = "SELECT * FROM fact" + (" WHERE fact_code LIKE %s OR fact_name LIKE %s" if q else "") + " ORDER BY fact_code"
    rows = query(sql, (f"%{q}%", f"%{q}%") if q else None)

    if st.session_state.adding:
        def do_add(v):
            try:
                execute("INSERT INTO fact VALUES (%s,%s,%s)", (v["fact_code"], v["fact_name"], v["remark"]))
                st.session_state.adding = False; st.toast("新增成功 ✅"); st.rerun()
            except Exception as e: st.error(str(e))
        show_form("新增廠商", fields, {}, do_add)

    elif st.session_state.edit:
        def do_edit(v):
            execute("UPDATE fact SET fact_name=%s, remark=%s WHERE fact_code=%s",
                    (v["fact_name"], v["remark"], v["fact_code"]))
            st.session_state.edit = None; st.toast("修改成功 ✅"); st.rerun()
        show_form("修改廠商", fields, st.session_state.edit, do_edit, disabled_keys=["fact_code"])

    def on_edit(row): st.session_state.edit = dict(row); st.session_state.adding = False; st.rerun()
    def on_del(pk):
        execute("DELETE FROM fact WHERE fact_code=%s", (pk,)); st.toast("已刪除"); st.rerun()
    render_table(rows, ["fact_code","fact_name","remark"], ["廠商代碼","廠商名稱","備註"], "f", on_edit, on_del)

# ── ITEM ─────────────────────────────────────────────────────────────────────

def item_page():
    back_btn("商品資料維護", "📦")

    col1, col2 = st.columns([4, 1])
    q = col1.text_input("", placeholder="🔍 搜尋代碼 / 名稱", label_visibility="collapsed", key="item_q")
    if col2.button("＋ 新增", key="item_add", use_container_width=True):
        st.session_state.adding = True; st.session_state.edit = None

    sql = """SELECT i.item_code, i.item_name, i.fact_code, f.fact_name
             FROM item i LEFT JOIN fact f ON i.fact_code=f.fact_code"""
    sql += (" WHERE i.item_code LIKE %s OR i.item_name LIKE %s" if q else "") + " ORDER BY i.item_code"
    rows = query(sql, (f"%{q}%", f"%{q}%") if q else None)

    facts = query("SELECT fact_code, fact_name FROM fact ORDER BY fact_code")
    fact_codes  = [f["fact_code"] for f in facts]
    fact_labels = [f"{f['fact_code']} {f['fact_name']}" for f in facts]
    fields = [("item_code","商品代碼","text"), ("item_name","商品名稱","text"),
              ("fact_code","主供應商","select", fact_codes, fact_labels)]

    if st.session_state.adding:
        def do_add(v):
            try:
                execute("INSERT INTO item VALUES (%s,%s,%s)", (v["item_code"], v["item_name"], v["fact_code"]))
                st.session_state.adding = False; st.toast("新增成功 ✅"); st.rerun()
            except Exception as e: st.error(str(e))
        show_form("新增商品", fields, {}, do_add)

    elif st.session_state.edit:
        def do_edit(v):
            execute("UPDATE item SET item_name=%s, fact_code=%s WHERE item_code=%s",
                    (v["item_name"], v["fact_code"], v["item_code"]))
            st.session_state.edit = None; st.toast("修改成功 ✅"); st.rerun()
        show_form("修改商品", fields, st.session_state.edit, do_edit, disabled_keys=["item_code"])

    display = [{**r, "supplier": f"{r['fact_code']} {r.get('fact_name','')}"} for r in rows]
    def on_edit(row): st.session_state.edit = dict(row); st.session_state.adding = False; st.rerun()
    def on_del(pk):
        execute("DELETE FROM item WHERE item_code=%s", (pk,)); st.toast("已刪除"); st.rerun()
    render_table(display, ["item_code","item_name","supplier"], ["商品代碼","商品名稱","主供應商"], "i", on_edit, on_del)

# ── USER ─────────────────────────────────────────────────────────────────────

def user_page():
    back_btn("用戶資料維護", "🔑")
    fields = [("userid","用戶代碼","text"), ("username","用戶名稱","text"), ("pwd","密碼","text")]

    col1, col2 = st.columns([4, 1])
    q = col1.text_input("", placeholder="🔍 搜尋代碼 / 名稱", label_visibility="collapsed", key="user_q")
    if col2.button("＋ 新增", key="user_add", use_container_width=True):
        st.session_state.adding = True; st.session_state.edit = None

    sql = "SELECT userid, username, pwd FROM [user]" + \
          (" WHERE userid LIKE %s OR username LIKE %s" if q else "") + " ORDER BY userid"
    rows = query(sql, (f"%{q}%", f"%{q}%") if q else None)

    if st.session_state.adding:
        def do_add(v):
            try:
                execute("INSERT INTO [user] VALUES (%s,%s,%s)", (v["userid"], v["username"], v["pwd"]))
                st.session_state.adding = False; st.toast("新增成功 ✅"); st.rerun()
            except Exception as e: st.error(str(e))
        show_form("新增用戶", fields, {}, do_add)

    elif st.session_state.edit:
        def do_edit(v):
            execute("UPDATE [user] SET username=%s, pwd=%s WHERE userid=%s",
                    (v["username"], v["pwd"], v["userid"]))
            st.session_state.edit = None; st.toast("修改成功 ✅"); st.rerun()
        show_form("修改用戶", fields, st.session_state.edit, do_edit, disabled_keys=["userid"])

    def on_edit(row): st.session_state.edit = dict(row); st.session_state.adding = False; st.rerun()
    def on_del(pk):
        execute("DELETE FROM [user] WHERE userid=%s", (pk,)); st.toast("已刪除"); st.rerun()
    render_table(rows, ["userid","username","pwd"], ["用戶代碼","用戶名稱","密碼"], "u", on_edit, on_del)

# ── Router ───────────────────────────────────────────────────────────────────

if not st.session_state.user:
    login_page()
else:
    {"main": main_page, "cust": cust_page, "fact": fact_page,
     "item": item_page, "user": user_page}.get(st.session_state.page, main_page)()
