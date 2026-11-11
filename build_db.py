import ijson, sqlite3

print("Starting JSON to SQLite Conversion...")
db = sqlite3.connect("data.db")
db.execute("PRAGMA journal_mode=OFF")
db.execute("PRAGMA synchronous=OFF")
db.execute("CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, phone TEXT, username TEXT, fname TEXT, lname TEXT)")

with open("Telegram_70M.json", "rb") as f:
    parser = ijson.items(f, 'item')
    batch = []
    count = 0
    for item in parser:
        batch.append((
            str(item.get('account_id', '')), str(item.get('phone', '')), 
            str(item.get('username', '')), str(item.get('first_name', '')), 
            str(item.get('last_name', ''))
        ))
        count += 1
        if len(batch) >= 100000:
            db.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)", batch)
            db.commit()
            batch.clear()
            print(f"Processed {count} records...")
            
    if batch:
        db.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)", batch)
        db.commit()

print("Creating Fast Search Indices...")
db.execute("CREATE INDEX IF NOT EXISTS idx_phone ON users(phone)")
db.execute("CREATE INDEX IF NOT EXISTS idx_username ON users(username)")
db.execute("CREATE INDEX IF NOT EXISTS idx_id ON users(id)")
db.commit()
db.close()
print("Database Ready!")
