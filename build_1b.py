import os, sqlite3, csv, sys
os.system("apt-get install p7zip-full -y > /dev/null 2>&1")
os.system("pip install huggingface_hub -q")

url1 = "https://huggingface.co/datasets/Rajunknown19/Tg-api_/resolve/main/telegram_1_billion.7z.001"
url2 = "https://huggingface.co/datasets/Rajunknown19/Tg-api_/resolve/main/telegram_1_billion.7z.002"

print("Downloading files...")
os.system(f"wget -q {url1} -O part1.7z.001")
os.system(f"wget -q {url2} -O part1.7z.002")

print("Extracting files...")
os.system("7z x part1.7z.001 -y > /dev/null")

files = [f for f in os.listdir('.') if f.endswith('.csv')]
if len(files) == 0:
    print("Error: Koi CSV file nahi mili.")
    sys.exit()

csv_file = files[0]
print(f"Data file mili: {csv_file}")

print("Building Database (1-2 ghante lagenge)...")
db = sqlite3.connect("data.db")
db.execute("PRAGMA journal_mode=OFF")
db.execute("PRAGMA synchronous=OFF")
db.execute("PRAGMA temp_store=FILE")
db.execute("CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, phone TEXT, username TEXT, fname TEXT, lname TEXT)")

with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    batch = []
    count = 0
    for row in reader:
        if len(row) >= 5:
            batch.append((row[0], row[1], row[2], row[3], row[4]))
            count += 1
        
        if len(batch) >= 100000:
            db.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)", batch)
            db.commit()
            batch.clear()
            print(f"Processed {count} records...", flush=True)
            
    if batch:
        db.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)", batch)
        db.commit()

print("Creating Indexes...")
db.execute("CREATE INDEX IF NOT EXISTS idx_phone ON users(phone)")
db.execute("CREATE INDEX IF NOT EXISTS idx_username ON users(username)")
db.commit()
db.close()

print("Compressing Database...")
os.system("7z a -mx=1 data.db.7z data.db > /dev/null")
os.system("rm data.db")

print("Uploading to Hugging Face...")
from huggingface_hub import login, HfApi
login(token="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") 

api = HfApi()
api.upload_file(
    path_or_fileobj="data.db.7z",
    path_in_repo="data.db.7z",
    repo_id="Rajunknown19/Tg-api_", 
    repo_type="dataset"
)
print("Upload Successful!")
