const initSqlJs = require('sql.js');
const fs = require('fs');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'glossary.db');
let db = null;

// Инициализация базы данных
async function initDB() {
  const SQL = await initSqlJs();

  // Попытка загрузить существующую БД
  if (fs.existsSync(dbPath)) {
    const buffer = fs.readFileSync(dbPath);
    db = new SQL.Database(buffer);
  } else {
    db = new SQL.Database();
  }

  // Создание таблицы при инициализации
  db.run(`
    CREATE TABLE IF NOT EXISTS terms (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      term TEXT UNIQUE NOT NULL,
      definition TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    )
  `);

  saveDB();
}

// Сохранение БД на диск
function saveDB() {
  if (db) {
    const data = db.export();
    fs.writeFileSync(dbPath, data);
  }
}

// Инициализация при загрузке модуля
initDB().catch((err) => console.error('DB init error:', err));

/**
 * Получить все термины
 */
function getAllTerms() {
  if (!db) return [];
  const result = db.exec('SELECT * FROM terms ORDER BY created_at DESC');
  if (result.length === 0) return [];

  const rows = result[0];
  return rows.values.map((row) => ({
    id: row[0],
    term: row[1],
    definition: row[2],
    created_at: row[3],
    updated_at: row[4],
  }));
}

/**
 * Получить термин по ключевому слову
 */
function getTermByName(termName) {
  if (!db) return null;
  const result = db.exec('SELECT * FROM terms WHERE term = ?', [termName]);
  if (result.length === 0 || result[0].values.length === 0) return null;

  const row = result[0].values[0];
  return {
    id: row[0],
    term: row[1],
    definition: row[2],
    created_at: row[3],
    updated_at: row[4],
  };
}

/**
 * Создать новый термин
 */
function createTerm(termName, definition) {
  if (!db) return null;

  try {
    db.run('INSERT INTO terms (term, definition) VALUES (?, ?)', [termName, definition]);
    saveDB();

    const result = db.exec('SELECT last_insert_rowid()');
    const lastId = result[0].values[0][0];
    return getTermById(lastId);
  } catch (error) {
    if (error.message && error.message.includes('UNIQUE')) {
      return null; // Термин уже существует
    }
    throw error;
  }
}

/**
 * Получить термин по ID
 */
function getTermById(id) {
  if (!db) return null;
  const result = db.exec('SELECT * FROM terms WHERE id = ?', [id]);
  if (result.length === 0 || result[0].values.length === 0) return null;

  const row = result[0].values[0];
  return {
    id: row[0],
    term: row[1],
    definition: row[2],
    created_at: row[3],
    updated_at: row[4],
  };
}

/**
 * Обновить термин
 */
function updateTerm(termName, newDefinition) {
  if (!db) return null;

  db.run(`UPDATE terms SET definition = ?, updated_at = datetime('now') WHERE term = ?`, [
    newDefinition,
    termName,
  ]);

  const changes = db.getRowsModified();
  saveDB();

  if (changes === 0) {
    return null; // Термин не найден
  }

  return getTermByName(termName);
}

/**
 * Удалить термин
 */
function deleteTerm(termName) {
  if (!db) return false;

  db.run('DELETE FROM terms WHERE term = ?', [termName]);
  const changes = db.getRowsModified();
  saveDB();

  return changes > 0;
}

module.exports = {
  getAllTerms,
  getTermByName,
  createTerm,
  updateTerm,
  deleteTerm,
};
