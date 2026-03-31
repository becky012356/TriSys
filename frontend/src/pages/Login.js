import { useState } from 'react';
import { apiFetch } from '../api';

export default function Login({ onLogin }) {
  const [form, setForm] = useState({ userid: '', pwd: '' });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const res = await apiFetch('/login', {
      method: 'POST',
      body: JSON.stringify(form)
    });
    if (res.ok) {
      onLogin(res.user);
    } else {
      setError(res.message);
    }
  };

  return (
    <div className="login-page">
      <div className="login-box">
        <h1>TriSys 系統</h1>
        <form onSubmit={handleSubmit}>
          <input
            placeholder="用戶代碼"
            value={form.userid}
            onChange={e => setForm({ ...form, userid: e.target.value })}
            required
          />
          <input
            type="password"
            placeholder="密碼"
            value={form.pwd}
            onChange={e => setForm({ ...form, pwd: e.target.value })}
            required
          />
          <button type="submit">登入</button>
        </form>
        {error && <div className="error-msg">{error}</div>}
      </div>
    </div>
  );
}
