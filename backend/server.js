const express = require('express');
const cors = require('cors');
const sql = require('mssql');
const dbConfig = require('./config');

const custRouter = require('./routes/cust');
const factRouter = require('./routes/fact');
const itemRouter = require('./routes/item');
const userRouter = require('./routes/user');

const app = express();
app.use(cors());
app.use(express.json());

// Connect to DB and attach pool to app
sql.connect(dbConfig).then(pool => {
  app.locals.db = pool;
  console.log('DB connected');
}).catch(err => {
  console.error('DB connection failed:', err.message);
});

app.use('/api/cust', custRouter);
app.use('/api/fact', factRouter);
app.use('/api/item', itemRouter);
app.use('/api/user', userRouter);

// Login
app.post('/api/login', async (req, res) => {
  const { userid, pwd } = req.body;
  try {
    const result = await req.app.locals.db.request()
      .input('userid', sql.VarChar, userid)
      .input('pwd', sql.VarChar, pwd)
      .query('SELECT userid, username FROM [user] WHERE userid=@userid AND pwd=@pwd');
    if (result.recordset.length > 0) {
      res.json({ ok: true, user: result.recordset[0] });
    } else {
      res.json({ ok: false, message: '帳號或密碼錯誤' });
    }
  } catch (err) {
    res.status(500).json({ ok: false, message: err.message });
  }
});

const PORT = 3001;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
