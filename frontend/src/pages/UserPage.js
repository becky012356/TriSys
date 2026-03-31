import { useState, useEffect } from 'react';
import { apiFetch } from '../api';

export default function UserPage() {
  const [data, setData] = useState([]);
  const [q, setQ] = useState('');
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({ userid: '', username: '', pwd: '' });

  const load = async (search = '') => {
    const res = await apiFetch('/user' + (search ? `?q=${search}` : ''));
    setData(res);
  };

  useEffect(() => { load(); }, []);

  const openAdd = () => { setForm({ userid: '', username: '', pwd: '' }); setModal('add'); };
  const openEdit = (row) => { setForm(row); setModal('edit'); };

  const save = async () => {
    if (modal === 'add') {
      await apiFetch('/user', { method: 'POST', body: JSON.stringify(form) });
    } else {
      await apiFetch(`/user/${form.userid}`, { method: 'PUT', body: JSON.stringify(form) });
    }
    setModal(null);
    load(q);
  };

  const del = async (id) => {
    if (!window.confirm(`確定刪除 ${id}？`)) return;
    await apiFetch(`/user/${id}`, { method: 'DELETE' });
    load(q);
  };

  return (
    <div className="crud-page">
      <h2>用戶資料維護</h2>
      <div className="search-bar">
        <input placeholder="搜尋代碼/名稱" value={q} onChange={e => setQ(e.target.value)} />
        <button onClick={() => load(q)}>搜尋</button>
      </div>
      <button className="add-btn" onClick={openAdd}>+ 新增</button>
      <div className="table-wrap">
        <table>
          <thead><tr><th>用戶代碼</th><th>用戶名稱</th><th>密碼</th><th>操作</th></tr></thead>
          <tbody>
            {data.map(r => (
              <tr key={r.userid}>
                <td>{r.userid}</td><td>{r.username}</td><td>{r.pwd}</td>
                <td>
                  <button className="action-btn edit-btn" onClick={() => openEdit(r)}>修改</button>
                  <button className="action-btn del-btn" onClick={() => del(r.userid)}>刪除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="modal-bg">
          <div className="modal">
            <h3>{modal === 'add' ? '新增用戶' : '修改用戶'}</h3>
            <label>用戶代碼</label>
            <input value={form.userid} disabled={modal === 'edit'}
              onChange={e => setForm({ ...form, userid: e.target.value })} />
            <label>用戶名稱</label>
            <input value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
            <label>密碼</label>
            <input value={form.pwd} onChange={e => setForm({ ...form, pwd: e.target.value })} />
            <div className="modal-btns">
              <button className="btn-save" onClick={save}>儲存</button>
              <button className="btn-cancel" onClick={() => setModal(null)}>取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
