CREATE TABLE IF NOT EXISTS universities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  country TEXT,
  city TEXT,
  website TEXT
);

CREATE TABLE IF NOT EXISTS aliases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  alias TEXT NOT NULL,
  university_id INTEGER NOT NULL,
  FOREIGN KEY (university_id) REFERENCES universities(id)
);

CREATE TABLE IF NOT EXISTS tuition_costs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  university_id INTEGER NOT NULL,
  tuition REAL,
  housing REAL,
  living_cost REAL,
  application_fee REAL,
  source TEXT,
  last_updated TEXT,
  FOREIGN KEY (university_id) REFERENCES universities(id)
);

CREATE TABLE IF NOT EXISTS salary_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  university_id INTEGER NOT NULL,
  median_salary REAL,
  average_debt REAL,
  roi_score REAL,
  FOREIGN KEY (university_id) REFERENCES universities(id)
);

CREATE TABLE IF NOT EXISTS rag_documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id TEXT UNIQUE NOT NULL,
  university TEXT,
  title TEXT,
  source_url TEXT,
  category TEXT,
  full_text TEXT,
  checksum TEXT,
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS rag_chunks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chunk_id TEXT UNIQUE NOT NULL,
  doc_id INTEGER NOT NULL,
  chunk_text TEXT,
  created_at TEXT,
  FOREIGN KEY (doc_id) REFERENCES rag_documents(id)
);

CREATE INDEX IF NOT EXISTS idx_aliases_alias ON aliases(alias);
CREATE INDEX IF NOT EXISTS idx_tuition_university ON tuition_costs(university_id);
CREATE INDEX IF NOT EXISTS idx_salary_university ON salary_data(university_id);
CREATE INDEX IF NOT EXISTS idx_rag_documents_doc_id ON rag_documents(doc_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_doc_id ON rag_chunks(doc_id);
