const express = require('express');
const sql = require('mssql');
const router = express.Router();

router.get('/', async (req, res) => {
  const { q } = req.query;
  let query = 'SELECT userid, username, pwd FROM [user]';
  if (q) query += ` WHERE userid LIKE @q OR username LIKE @q`;
  query += ' ORDER BY userid';
  try {
    const req2 = req.app.locals.db.request();
    if (q) req2.input('q', sql.NVarChar, `%${q}%`);
    const result = await req2.query(query);
    res.json(result.recordset);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.post('/', async (req, res) => {
  const { userid, username, pwd } = req.body;
  try {
    await req.app.locals.db.request()
      .input('userid', sql.VarChar, userid)
      .input('username', sql.NVarChar, username)
      .input('pwd', sql.VarChar, pwd)
      .query('INSERT INTO [user] VALUES (@userid, @username, @pwd)');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.put('/:id', async (req, res) => {
  const { username, pwd } = req.body;
  try {
    await req.app.locals.db.request()
      .input('userid', sql.VarChar, req.params.id)
      .input('username', sql.NVarChar, username)
      .input('pwd', sql.VarChar, pwd)
      .query('UPDATE [user] SET username=@username, pwd=@pwd WHERE userid=@userid');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    await req.app.locals.db.request()
      .input('userid', sql.VarChar, req.params.id)
      .query('DELETE FROM [user] WHERE userid=@userid');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;
