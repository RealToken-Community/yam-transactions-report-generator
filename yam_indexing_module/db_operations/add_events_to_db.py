import sqlite3
from typing import List, Dict
from .internal._event_handlers import _handle_offer_created, _handle_offer_accepted, _handle_offer_deleted, _handle_offer_updated
from .internal._db_operations import _update_indexing_state


def add_events_to_db(
    db_path: str,
    from_block: int,
    to_block: int,
    decoded_logs: List[Dict],
    initialisation_mode: bool = False
) -> None:
    """
    Add YAM events to a SQLite database, including offer creation, acceptance,
    updates, and deletions.
    
    The function processes different event types and updates the database accordingly:
    - OfferCreated: Adds a new offer to the 'offers' table
    - OfferAccepted: Records acceptance in 'offer_events' and updates offer status
    - OfferUpdated: Records update in 'offer_events' and sets offer status to 'InProgress'
    - OfferDeleted: Records deletion in 'offer_events' and sets offer status to 'Deleted'
    
    Finally, it updates the 'indexing_state' table to track which blocks have been processed.
    
    Args:
        db_path: Path to the SQLite database file
        from_block: Starting block number for this batch of events
        to_block: Ending block number for this batch of events
        decoded_logs: List of decoded blockchain event logs
        
    Returns:
        None
    """
    # Connect to the SQLite database (creates the database file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Process each event log
    for i, log in enumerate(decoded_logs):
        event_type = log['topic']
        
        if event_type == 'OfferCreated':
            _handle_offer_created(cursor, log)
        elif event_type == 'OfferAccepted':
            _handle_offer_accepted(cursor, log)
            conn.commit()  # Commit here to ensure status retrieval has latest data
        elif event_type == 'OfferUpdated':
            _handle_offer_updated(cursor, log)
        elif event_type == 'OfferDeleted':
            _handle_offer_deleted(cursor, log)
        
        # Show progress when initialising
        if initialisation_mode:
            # Clear the line first, then write new content
            print(f"\r" + " " * 70, end="", flush=True)  # Clear with spaces
            print(f"\r{i+1} events added to the DB out of {len(decoded_logs)}", end="", flush=True)
    
    if from_block is not None and to_block is not None:
        # Update the indexing state to track processed blocks
        _update_indexing_state(cursor, from_block, to_block)
    
    # Commit all changes and close the connection
    conn.commit()
    conn.close()