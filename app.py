import streamlit as st
import pymssql
import pandas as pd

st.set_page_config(page_title="TriSys", page_icon="📊", layout="centered")

# ── DB ──────────────────────────────────────────────────────────────────────

def get_conn():
    cfg = st.secrets["db"]
    return pymssql.connect(
        server=cfg["server"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"]
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

# ── Session state init ───────────────────────────────────────────────────────

def init():
    for k, v in [("user", None), ("page", "main"), ("edit", None), ("adding", False)]:
        if k not in st.session_state:
            st.session_state[k] = v

init()

# ── CSS ──────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
div[data-testid="stForm"] { border: none; padding: 0; }
.big-btn { font-size: 1.3rem !important; padding: 2rem 1rem !important; border-radius: 16px !important; }
</style>
""", unsafe_allow_html=True)

# ── Login ────────────────────────────────────────────────────────────────────

def login_page():
    st.markdown("<h1 style='text-align:center;color:#1a73e8;'>TriSys 系統</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        userid = st.text_input("用戶代碼")
        pwd    = st.text_input("密碼", type="password")
        ok     = st.form_submit_button("登入", use_container_width=True)
    if ok:
        rows = query("SELECT userid, username FROM [user] WHERE userid=%s AND pwd=%s", (userid, pwd))
        if rows:
            st.session_state.user = rows[0]
            st.rerun()
        else:
            st.error("帳號或密碼錯誤")

# ── Main menu ────────────────────────────────────────────────────────────────

def main_page():
    c1, c2 = st.columns([5, 1])
    c1.markdown(f"### 歡迎，{st.session_state.user['username']}")
    if c2.button("登出"):
        st.session_state.user = None
        st.rerun()

    st.markdown("---")
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

# ── Generic CRUD helpers ─────────────────────────────────────────────────────

def back_btn():
    if st.button("← 返回主選單"):
        st.session_state.page = "main"
        st.session_state.edit = None
        st.session_state.adding = False
        st.rerun()

def show_form(title, fields, defaults, on_save, disabled_keys=None):
    """fields: list of (key, label, type)  type: text|password|select"""
    st.subheader(title)
    vals = {}
    with st.form("crud_form"):
        for key, label, ftype, *extra in fields:
            default = defaults.get(key, "")
            dis = disabled_keys and key in disabled_keys
            if ftype == "select":
                options = extra[0] if extra else []
                labels  = extra[1] if len(extra) > 1 else options
                idx = options.index(default) if default in options else 0
                vals[key] = st.selectbox(label, options, index=idx,
                                         format_func=lambda x, o=options, l=labels: l[o.index(x)],
                                         disabled=dis)
            elif ftype == "password":
                vals[key] = st.text_input(label, value=default, disabled=dis)
            else:
                vals[key] = st.text_input(label, value=default, disabled=dis)
        c1, c2 = st.columns(2)
        saved   = c1.form_submit_button("儲存", use_container_width=True)
        cancel  = c2.form_submit_button("取消", use_container_width=True)
    if saved:
        on_save(vals)
    if cancel:
        st.session_state.edit = None
        st.session_state.adding = False
        st.rerun()

def show_table(rows, cols, key_col, on_edit, on_del):
    if not rows:
        st.info("無資料")
        return
    header = cols + ["操作"]
    hcols = st.columns([3]*len(cols) + [2])
    for i, h in enumerate(header):
        hcols[i].markdown(f"**{h}**")
    st.markdown("<hr style='margin:4px 0'>", unsafe_allow_html=True)
    for row in rows:
        rcols = st.columns([3]*len(cols) + [2])
        for i, col in enumerate(cols):
            rcols[i].write(row.get(list(row.keys())[i], ""))
        with rcols[-1]:
            c1, c2 = st.columns(2)
            if c1.button("修改", key=f"e_{row[key_col]}"):
                on_edit(row)
            if c2.button("刪除", key=f"d_{row[key_col]}"):
                on_del(row[key_col])

# ── CUST ─────────────────────────────────────────────────────────────────────

def cust_page():
    back_btn()
    st.title("客戶資料維護")

    q = st.text_input("搜尋代碼/名稱", key="cust_q")
    if st.button("+ 新增客戶", key="cust_add"):
        st.session_state.adding = True
        st.session_state.edit = None

    sql = "SELECT * FROM cust" + (" WHERE cust_code LIKE %s OR cust_name LIKE %s" if q else "") + " ORDER BY cust_code"
    rows = query(sql, (f"%{q}%", f"%{q}%") if q else None)
    fields = [("cust_code","客戶代碼","text"), ("cust_name","客戶名稱","text"), ("remark","備註","text")]

    if st.session_state.adding:
        def do_add(v):
            try:
                execute("INSERT INTO cust VALUES (%s,%s,%s)", (v["cust_code"], v["cust_name"], v["remark"]))
                st.session_state.adding = False
                st.success("新增成功"); st.rerun()
            except Exception as e:
                st.error(str(e))
        show_form("新增客戶", fields, {}, do_add)

    elif st.session_state.edit:
        def do_edit(v):
            execute("UPDATE cust SET cust_name=%s, remark=%s WHERE cust_code=%s",
                    (v["cust_name"], v["remark"], v["cust_code"]))
            st.session_state.edit = None
            st.success("修改成功"); st.rerun()
        show_form("修改客戶", fields, st.session_state.edit, do_edit, disabled_keys=["cust_code"])

    st.markdown("---")
    for row in rows:
        c1, c2, c3, c4, c5 = st.columns([2, 3, 3, 1, 1])
        c1.write(row["cust_code"]); c2.write(row["cust_name"]); c3.write(row.get("remark",""))
        if c4.button("修改", key=f"ce_{row['cust_code']}"):
            st.session_state.edit = dict(row); st.session_state.adding = False; st.rerun()
        if c5.button("刪除", key=f"cd_{row['cust_code']}"):
            execute("DELETE FROM cust WHERE cust_code=%s", (row["cust_code"],)); st.rerun()

# ── FACT ─────────────────────────────────────────────────────────────────────

def fact_page():
    back_btn()
    st.title("廠商資料維護")

    q = st.text_input("搜尋代碼/名稱", key="fact_q")
    if st.button("+ 新增廠商", key="fact_add"):
        st.session_state.adding = True
        st.session_state.edit = None

    sql = "SELECT * FROM fact" + (" WHERE fact_code LIKE %s OR fact_name LIKE %s" if q else "") + " ORDER BY fact_code"
    rows = query(sql, (f"%{q}%", f"%{q}%") if q else None)
    fields = [("fact_code","廠商代碼","text"), ("fact_name","廠商名稱","text"), ("remark","備註","text")]

    if st.session_state.adding:
        def do_add(v):
            try:
                execute("INSERT INTO fact VALUES (%s,%s,%s)", (v["fact_code"], v["fact_name"], v["remark"]))
                st.session_state.adding = False
                st.success("新增成功"); st.rerun()
            except Exception as e:
                st.error(str(e))
        show_form("新增廠商", fields, {}, do_add)

    elif st.session_state.edit:
        def do_edit(v):
            execute("UPDATE fact SET fact_name=%s, remark=%s WHERE fact_code=%s",
                    (v["fact_name"], v["remark"], v["fact_code"]))
            st.session_state.edit = None
            st.success("修改成功"); st.rerun()
        show_form("修改廠商", fields, st.session_state.edit, do_edit, disabled_keys=["fact_code"])

    st.markdown("---")
    for row in rows:
        c1, c2, c3, c4, c5 = st.columns([2, 3, 3, 1, 1])
        c1.write(row["fact_code"]); c2.write(row["fact_name"]); c3.write(row.get("remark",""))
        if c4.button("修改", key=f"fe_{row['fact_code']}"):
            st.session_state.edit = dict(row); st.session_state.adding = False; st.rerun()
        if c5.button("刪除", key=f"fd_{row['fact_code']}"):
            execute("DELETE FROM fact WHERE fact_code=%s", (row["fact_code"],)); st.rerun()

# ── ITEM ─────────────────────────────────────────────────────────────────────

def item_page():
    back_btn()
    st.title("商品資料維護")

    q = st.text_input("搜尋代碼/名稱", key="item_q")
    if st.button("+ 新增商品", key="item_add"):
        st.session_state.adding = True
        st.session_state.edit = None

    sql = """SELECT i.item_code, i.item_name, i.fact_code, f.fact_name
             FROM item i LEFT JOIN fact f ON i.fact_code=f.fact_code"""
    if q:
        sql += " WHERE i.item_code LIKE %s OR i.item_name LIKE %s"
    sql += " ORDER BY i.item_code"
    rows = query(sql, (f"%{q}%", f"%{q}%") if q else None)

    facts = query("SELECT fact_code, fact_name FROM fact ORDER BY fact_code")
    fact_codes  = [f["fact_code"] for f in facts]
    fact_labels = [f"{f['fact_code']} {f['fact_name']}" for f in facts]
    fields = [
        ("item_code","商品代碼","text"),
        ("item_name","商品名稱","text"),
        ("fact_code","主供應商","select", fact_codes, fact_labels)
    ]

    if st.session_state.adding:
        def do_add(v):
            try:
                execute("INSERT INTO item VALUES (%s,%s,%s)", (v["item_code"], v["item_name"], v["fact_code"]))
                st.session_state.adding = False
                st.success("新增成功"); st.rerun()
            except Exception as e:
                st.error(str(e))
        show_form("新增商品", fields, {}, do_add)

    elif st.session_state.edit:
        def do_edit(v):
            execute("UPDATE item SET item_name=%s, fact_code=%s WHERE item_code=%s",
                    (v["item_name"], v["fact_code"], v["item_code"]))
            st.session_state.edit = None
            st.success("修改成功"); st.rerun()
        show_form("修改商品", fields, st.session_state.edit, do_edit, disabled_keys=["item_code"])

    st.markdown("---")
    for row in rows:
        c1, c2, c3, c4, c5 = st.columns([2, 3, 3, 1, 1])
        c1.write(row["item_code"]); c2.write(row["item_name"])
        c3.write(f"{row['fact_code']} {row.get('fact_name','')}")
        if c4.button("修改", key=f"ie_{row['item_code']}"):
            st.session_state.edit = dict(row); st.session_state.adding = False; st.rerun()
        if c5.button("刪除", key=f"id_{row['item_code']}"):
            execute("DELETE FROM item WHERE item_code=%s", (row["item_code"],)); st.rerun()

# ── USER ─────────────────────────────────────────────────────────────────────

def user_page():
    back_btn()
    st.title("用戶資料維護")

    q = st.text_input("搜尋代碼/名稱", key="user_q")
    if st.button("+ 新增用戶", key="user_add"):
        st.session_state.adding = True
        st.session_state.edit = None

    sql = "SELECT userid, username, pwd FROM [user]" + \
          (" WHERE userid LIKE %s OR username LIKE %s" if q else "") + " ORDER BY userid"
    rows = query(sql, (f"%{q}%", f"%{q}%") if q else None)
    fields = [("userid","用戶代碼","text"), ("username","用戶名稱","text"), ("pwd","密碼","text")]

    if st.session_state.adding:
        def do_add(v):
            try:
                execute("INSERT INTO [user] VALUES (%s,%s,%s)", (v["userid"], v["username"], v["pwd"]))
                st.session_state.adding = False
                st.success("新增成功"); st.rerun()
            except Exception as e:
                st.error(str(e))
        show_form("新增用戶", fields, {}, do_add)

    elif st.session_state.edit:
        def do_edit(v):
            execute("UPDATE [user] SET username=%s, pwd=%s WHERE userid=%s",
                    (v["username"], v["pwd"], v["userid"]))
            st.session_state.edit = None
            st.success("修改成功"); st.rerun()
        show_form("修改用戶", fields, st.session_state.edit, do_edit, disabled_keys=["userid"])

    st.markdown("---")
    for row in rows:
        c1, c2, c3, c4, c5 = st.columns([2, 3, 3, 1, 1])
        c1.write(row["userid"]); c2.write(row["username"]); c3.write(row["pwd"])
        if c4.button("修改", key=f"ue_{row['userid']}"):
            st.session_state.edit = dict(row); st.session_state.adding = False; st.rerun()
        if c5.button("刪除", key=f"ud_{row['userid']}"):
            execute("DELETE FROM [user] WHERE userid=%s", (row["userid"],)); st.rerun()

# ── Router ────────────────────────────────────────────────────────────────────

if not st.session_state.user:
    login_page()
else:
    pages = {"main": main_page, "cust": cust_page, "fact": fact_page, "item": item_page, "user": user_page}
    pages.get(st.session_state.page, main_page)()
