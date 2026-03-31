export default function Main({ user, onNav, onLogout }) {
  return (
    <div className="main-page">
      <div className="main-header">
        <h2>歡迎，{user.username}</h2>
        <button className="logout-btn" onClick={onLogout}>登出</button>
      </div>
      <div className="grid">
        <button className="grid-btn btn-cust" onClick={() => onNav('cust')}>
          <span className="icon">👥</span>客戶資料
        </button>
        <button className="grid-btn btn-fact" onClick={() => onNav('fact')}>
          <span className="icon">🏭</span>廠商資料
        </button>
        <button className="grid-btn btn-item" onClick={() => onNav('item')}>
          <span className="icon">📦</span>商品資料
        </button>
        <button className="grid-btn btn-user" onClick={() => onNav('user')}>
          <span className="icon">🔑</span>用戶管理
        </button>
      </div>
    </div>
  );
}
