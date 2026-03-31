const express = require('express');
const sql = require('mssql');
const router = express.Router();

// Query
router.get('/', async (req, res) => {
  const { q } = req.query;
  let query = 'SELECT * FROM cust';
  if (q) query += ` WHERE cust_code LIKE @q OR cust_name LIKE @q`;
  query += ' ORDER BY cust_code';
  try {
    const req2 = req.app.locals.db.request();
    if (q) req2.input('q', sql.NVarChar, `%${q}%`);
    const result = await req2.query(query);
    res.json(result.recordset);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Create
router.post('/', async (req, res) => {
  const { cust_code, cust_name, remark } = req.body;
  try {
    await req.app.locals.db.request()
      .input('cust_code', sql.VarChar, cust_code)
      .input('cust_name', sql.NVarChar, cust_name)
      .input('remark', sql.NVarChar, remark)
      .query('INSERT INTO cust VALUES (@cust_code, @cust_name, @remark)');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Update
router.put('/:code', async (req, res) => {
  const { cust_name, remark } = req.body;
  try {
    await req.app.locals.db.request()
      .input('cust_code', sql.VarChar, req.params.code)
      .input('cust_name', sql.NVarChar, cust_name)
      .input('remark', sql.NVarChar, remark)
      .query('UPDATE cust SET cust_name=@cust_name, remark=@remark WHERE cust_code=@cust_code');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Delete
router.delete('/:code', async (req, res) => {
  try {
    await req.app.locals.db.request()
      .input('cust_code', sql.VarChar, req.params.code)
      .query('DELETE FROM cust WHERE cust_code=@cust_code');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;
