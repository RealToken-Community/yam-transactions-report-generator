import sqlite3

def init_db(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    print("Creating database tables...")

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS offers (
        offer_id INTEGER PRIMARY KEY,
        seller_address TEXT NOT NULL,
        initial_amount TEXT NOT NULL,
        price_per_unit TEXT NOT NULL,
        offer_token TEXT NOT NULL,
        buyer_token TEXT NOT NULL,
        status TEXT CHECK (status IN ('InProgress', 'SoldOut', 'Deleted') ) DEFAULT 'InProgress',
        block_number INTEGER NOT NULL,
        transaction_hash TEXT NOT NULL,
        log_index INTEGER NOT NULL,
        creation_timestamp DATETIME
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS offer_events (
        offer_id INTEGER NOT NULL,
        event_type TEXT NOT NULL CHECK (event_type IN ('OfferCreated', 'OfferUpdated', 'OfferAccepted', 'OfferDeleted')),
        amount TEXT,
        price TEXT,
        buyer_address TEXT,
        amount_bought TEXT,
        block_number INTEGER NOT NULL,
        transaction_hash TEXT NOT NULL,
        log_index INTEGER NOT NULL,
        price_bought TEXT,
        event_timestamp DATETIME,
        unique_id TEXT PRIMARY KEY NOT NULL,
        FOREIGN KEY (offer_id) REFERENCES offers (offer_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS indexing_state (
        indexing_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        from_block INTEGER NOT NULL,
        to_block INTEGER NOT NULL
    );
    """)

    # Create indexes for query optimization
    print("Creating database indexes...")
    
    # Composite index for offer_events filtering (most important)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_offer_events_type_timestamp 
    ON offer_events (event_type, event_timestamp);
    """)

    # Index for buyer address filtering
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_offer_events_buyer_address 
    ON offer_events (buyer_address);
    """)

    # Index for seller address filtering  
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_offers_seller_address 
    ON offers (seller_address);
    """)

    # Foreign key index for JOIN optimization
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_offer_events_offer_id 
    ON offer_events (offer_id);
    """)

    conn.commit()
    conn.close()
    print("Database initialization completed.")

if __name__ == "__main__":
    import json
    with open('config.json', 'r') as f:
        DB_PATH = json.load(f)['db_path']
    init_db(DB_PATH)