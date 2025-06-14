import sqlite3

def _update_indexing_state(
    cursor: sqlite3.Cursor,
    from_block: int,
    to_block: int
) -> None:
    """
    Update the indexing state to track which blocks have been processed.
    
    Either extends the most recent entry if the new range is contiguous,
    or creates a new entry if there's a gap.
    
    Args:
        cursor: Database cursor
        from_block: Starting block number for this batch
        to_block: Ending block number for this batch
    """
    # Get the most recent indexing entry
    cursor.execute("SELECT * FROM indexing_state ORDER BY indexing_id DESC LIMIT 1")
    most_recent_entry = cursor.fetchone()
    
    # Determine if we should extend the existing entry or create a new one
    if most_recent_entry is not None:
        # Check if new range is contiguous with existing range
        if most_recent_entry[1] <= from_block <= most_recent_entry[2] + 1 and to_block > most_recent_entry[2]:
            # Extend the existing entry
            cursor.execute(
                "UPDATE indexing_state SET to_block = ? WHERE indexing_id = ?",
                (to_block, most_recent_entry[0])
            )
            return
    
    # If we reach here, we either need to create a new entry or no update is needed
    if most_recent_entry is None or to_block > most_recent_entry[2]:
        cursor.execute(
            "INSERT INTO indexing_state (from_block, to_block) VALUES (?, ?)",
            (from_block, to_block)
        )

def _get_last_indexed_block(db_path):
    """
    Get the last indexed block number from the database.
    
    Args:
        db_path (str): Path to the SQLite database file
        
    Returns:
        int: The last indexed block number, or None if no records found
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT to_block FROM indexing_state ORDER BY indexing_id DESC LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            return None
        
    finally:
        conn.close()