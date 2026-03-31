import { useState, useEffect } from 'react';
import { apiFetch } from '../api';

export default function ItemPage() {
  const [data, setData] = useState([]);
  const [facts, setFacts] = useState([]);
  const [q, setQ] = useState('');
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({ item_code: '', item_name: '', fact_code: '' });

  const load = async (search = '') => {
    const res = await apiFetch('/item' + (search ? `?q=${search}` : ''));
    setData(res);
  };

  useEffect(() => {
    load();
    apiFetch('/fact').then(setFacts);
  }, []);

  const openAdd = () => { setForm({ item_code: '', item_name: '', fact_code: '' }); setModal('add'); };
  const openEdit = (row) => { setForm(row); setModal('edit'); };

  const save = async () => {
    if (modal === 'add') {
      await apiFetch('/item', { method: 'POST', body: JSON.stringify(form) });
    } else {
      await apiFetch(`/item/${form.item_code}`, { method: 'PUT', body: JSON.stringify(form) });
    }
    setModal(null);
    load(q);
  };

  const del = async (code) => {
    if (!window.confirm(`確定刪除 ${code}？`)) return;
    await apiFetch(`/item/${code}`, { method: 'DELETE' });
    load(q);
  };

  return (
    <div className="crud-page">
      <h2>商品資料維護</h2>
      <div className="search-bar">
        <input placeholder="搜尋代碼/名稱" value={q} onChange={e => setQ(e.target.value)} />
        <button onClick={() => load(q)}>搜尋</button>
      </div>
      <button className="add-btn" onClick={openAdd}>+ 新增</button>
      <div className="table-wrap">
        <table>
          <thead><tr><th>商品代碼</th><th>商品名稱</th><th>主供應商</th><th>操作</th></tr></thead>
          <tbody>
            {data.map(r => (
              <tr key={r.item_code}>
                <td>{r.item_code}</td><td>{r.item_name}</td><td>{r.fact_name || r.fact_code}</td>
                <td>
                  <button className="action-btn edit-btn" onClick={() => openEdit(r)}>修改</button>
                  <button className="action-btn del-btn" onClick={() => del(r.item_code)}>刪除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="modal-bg">
          <div className="modal">
            <h3>{modal === 'add' ? '新增商品' : '修改商品'}</h3>
            <label>商品代碼</label>
            <input value={form.item_code} disabled={modal === 'edit'}
              onChange={e => setForm({ ...form, item_code: e.target.value })} />
            <label>商品名稱</label>
            <input value={form.item_name} onChange={e => setForm({ ...form, item_name: e.target.value })} />
            <label>主供應商</label>
            <select value={form.fact_code} onChange={e => setForm({ ...form, fact_code: e.target.value })}>
              <option value="">-- 請選擇 --</option>
              {facts.map(f => <option key={f.fact_code} value={f.fact_code}>{f.fact_code} {f.fact_name}</option>)}
            </select>
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
