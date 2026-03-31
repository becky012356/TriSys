const express = require('express');
const sql = require('mssql');
const router = express.Router();

router.get('/', async (req, res) => {
  const { q } = req.query;
  let query = 'SELECT i.*, f.fact_name FROM item i LEFT JOIN fact f ON i.fact_code=f.fact_code';
  if (q) query += ` WHERE i.item_code LIKE @q OR i.item_name LIKE @q`;
  query += ' ORDER BY i.item_code';
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
  const { item_code, item_name, fact_code } = req.body;
  try {
    await req.app.locals.db.request()
      .input('item_code', sql.VarChar, item_code)
      .input('item_name', sql.NVarChar, item_name)
      .input('fact_code', sql.VarChar, fact_code)
      .query('INSERT INTO item VALUES (@item_code, @item_name, @fact_code)');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.put('/:code', async (req, res) => {
  const { item_name, fact_code } = req.body;
  try {
    await req.app.locals.db.request()
      .input('item_code', sql.VarChar, req.params.code)
      .input('item_name', sql.NVarChar, item_name)
      .input('fact_code', sql.VarChar, fact_code)
      .query('UPDATE item SET item_name=@item_name, fact_code=@fact_code WHERE item_code=@item_code');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.delete('/:code', async (req, res) => {
  try {
    await req.app.locals.db.request()
      .input('item_code', sql.VarChar, req.params.code)
      .query('DELETE FROM item WHERE item_code=@item_code');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;
