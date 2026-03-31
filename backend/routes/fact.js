const express = require('express');
const sql = require('mssql');
const router = express.Router();

router.get('/', async (req, res) => {
  const { q } = req.query;
  let query = 'SELECT * FROM fact';
  if (q) query += ` WHERE fact_code LIKE @q OR fact_name LIKE @q`;
  query += ' ORDER BY fact_code';
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
  const { fact_code, fact_name, remark } = req.body;
  try {
    await req.app.locals.db.request()
      .input('fact_code', sql.VarChar, fact_code)
      .input('fact_name', sql.NVarChar, fact_name)
      .input('remark', sql.NVarChar, remark)
      .query('INSERT INTO fact VALUES (@fact_code, @fact_name, @remark)');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.put('/:code', async (req, res) => {
  const { fact_name, remark } = req.body;
  try {
    await req.app.locals.db.request()
      .input('fact_code', sql.VarChar, req.params.code)
      .input('fact_name', sql.NVarChar, fact_name)
      .input('remark', sql.NVarChar, remark)
      .query('UPDATE fact SET fact_name=@fact_name, remark=@remark WHERE fact_code=@fact_code');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.delete('/:code', async (req, res) => {
  try {
    await req.app.locals.db.request()
      .input('fact_code', sql.VarChar, req.params.code)
      .query('DELETE FROM fact WHERE fact_code=@fact_code');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;
