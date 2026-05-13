import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'outreach.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Runs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prospect_name TEXT,
            company_name TEXT,
            role TEXT,
            product_description TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Signals table
    c.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            signal_type TEXT,
            content TEXT,
            url TEXT,
            FOREIGN KEY (run_id) REFERENCES runs (id)
        )
    ''')
    
    # Drafts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            hook TEXT,
            email_subject TEXT,
            email_body TEXT,
            linkedin_draft TEXT,
            quality_score INTEGER,
            is_approved BOOLEAN DEFAULT 0,
            FOREIGN KEY (run_id) REFERENCES runs (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_run(prospect_name, company_name, role, product_description, status='Pending'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO runs (prospect_name, company_name, role, product_description, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (prospect_name, company_name, role, product_description, status))
    run_id = c.lastrowid
    conn.commit()
    conn.close()
    return run_id

def update_run_status(run_id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE runs SET status = ? WHERE id = ?', (status, run_id))
    conn.commit()
    conn.close()

def save_signals(run_id, signals):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for s in signals:
        c.execute('''
            INSERT INTO signals (run_id, signal_type, content, url)
            VALUES (?, ?, ?, ?)
        ''', (run_id, s.get('type'), s.get('content'), s.get('url')))
    conn.commit()
    conn.close()

def save_draft(run_id, hook, subject, body, linkedin, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO drafts (run_id, hook, email_subject, email_body, linkedin_draft, quality_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (run_id, hook, subject, body, linkedin, score))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT r.*, d.hook, d.email_subject, d.email_body, d.linkedin_draft, d.quality_score 
        FROM runs r 
        LEFT JOIN drafts d ON r.id = d.run_id 
        ORDER BY r.created_at DESC
    ''')
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
