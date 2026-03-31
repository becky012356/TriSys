import { useState } from 'react';
import Login from './pages/Login';
import Main from './pages/Main';
import CustPage from './pages/CustPage';
import FactPage from './pages/FactPage';
import ItemPage from './pages/ItemPage';
import UserPage from './pages/UserPage';
import './App.css';

export default function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState('main');

  if (!user) return <Login onLogin={u => { setUser(u); setPage('main'); }} />;

  const pages = { cust: <CustPage />, fact: <FactPage />, item: <ItemPage />, user: <UserPage /> };

  return (
    <div className="app">
      {page !== 'main' && (
        <button className="back-btn" onClick={() => setPage('main')}>← 返回</button>
      )}
      {page === 'main'
        ? <Main user={user} onNav={setPage} onLogout={() => setUser(null)} />
        : pages[page]}
    </div>
  );
}
