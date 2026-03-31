import { useState, useEffect } from 'react';
import { apiFetch } from '../api';

export default function FactPage() {
  const [data, setData] = useState([]);
  const [q, setQ] = useState('');
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({ fact_code: '', fact_name: '', remark: '' });

  const load = async (search = '') => {
    const res = await apiFetch('/fact' + (search ? `?q=${search}` : ''));
    setData(res);
  };

  useEffect(() => { load(); }, []);

  const openAdd = () => { setForm({ fact_code: '', fact_name: '', remark: '' }); setModal('add'); };
  const openEdit = (row) => { setForm(row); setModal('edit'); };

  const save = async () => {
    if (modal === 'add') {
      await apiFetch('/fact', { method: 'POST', body: JSON.stringify(form) });
    } else {
      await apiFetch(`/fact/${form.fact_code}`, { method: 'PUT', body: JSON.stringify(form) });
    }
    setModal(null);
    load(q);
  };

  const del = async (code) => {
    if (!window.confirm(`確定刪除 ${code}？`)) return;
    await apiFetch(`/fact/${code}`, { method: 'DELETE' });
    load(q);
  };

  return (
    <div className="crud-page">
      <h2>廠商資料維護</h2>
      <div className="search-bar">
        <input placeholder="搜尋代碼/名稱" value={q} onChange={e => setQ(e.target.value)} />
        <button onClick={() => load(q)}>搜尋</button>
      </div>
      <button className="add-btn" onClick={openAdd}>+ 新增</button>
      <div className="table-wrap">
        <table>
          <thead><tr><th>廠商代碼</th><th>廠商名稱</th><th>備註</th><th>操作</th></tr></thead>
          <tbody>
            {data.map(r => (
              <tr key={r.fact_code}>
                <td>{r.fact_code}</td><td>{r.fact_name}</td><td>{r.remark}</td>
                <td>
                  <button className="action-btn edit-btn" onClick={() => openEdit(r)}>修改</button>
                  <button className="action-btn del-btn" onClick={() => del(r.fact_code)}>刪除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="modal-bg">
          <div className="modal">
            <h3>{modal === 'add' ? '新增廠商' : '修改廠商'}</h3>
            <label>廠商代碼</label>
            <input value={form.fact_code} disabled={modal === 'edit'}
              onChange={e => setForm({ ...form, fact_code: e.target.value })} />
            <label>廠商名稱</label>
            <input value={form.fact_name} onChange={e => setForm({ ...form, fact_name: e.target.value })} />
            <label>備註</label>
            <input value={form.remark || ''} onChange={e => setForm({ ...form, remark: e.target.value })} />
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
