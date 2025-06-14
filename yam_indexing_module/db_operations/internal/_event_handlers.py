import sqlite3
from typing import Dict
from datetime import datetime
from web3 import Web3
from ._get_status_offer import _get_offer_status

def _get_timestamp_value(log: Dict) -> str:
    """
    Get timestamp value from log, either from Unix timestamp or current time.
    
    Args:
        log: Event log data
        
    Returns:
        Timestamp string in SQLite datetime format
    """
    if 'timestamp' in log and log['timestamp'] is not None:
        # Convert Unix timestamp to datetime string
        return datetime.fromtimestamp(int(log['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
    else:
        # Use current timestamp
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def _handle_offer_created(
    cursor: sqlite3.Cursor,
    log: Dict
) -> None:
    """
    Handle 'OfferCreated' event by inserting a new offer into the database.
    
    Args:
        cursor: Database cursor
        log: Event log data
    """
    # Get timestamp value
    timestamp_value = _get_timestamp_value(log)
    
    # Build the SQL query
    insert_query = """
        INSERT INTO offers (
            offer_id, seller_address, initial_amount, price_per_unit,
            offer_token, buyer_token, transaction_hash, block_number, log_index,
            creation_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        # Execute the query with data
        cursor.execute(
            insert_query,
            (
                log['offerId'],
                Web3.to_checksum_address(log['seller']),
                str(log['amount']),
                str(log['price']),
                Web3.to_checksum_address(log['offerToken']),
                Web3.to_checksum_address(log['buyerToken']),
                log['transactionHash'],
                log['blockNumber'],
                log['logIndex'],
                timestamp_value
            )
        )
    except sqlite3.IntegrityError as e:
        # Ignore duplicate entries -> silently skip already-added entries
        if 'UNIQUE constraint failed: offers.offer_id' not in str(e):
            raise e


def _handle_offer_accepted(
    cursor: sqlite3.Cursor,
    log: Dict
) -> None:
    """
    Handle 'OfferAccepted' event by recording acceptance and updating offer status.
    
    Args:
        cursor: Database cursor
        log: Event log data
    """
    # Create a unique ID for the primary key of the table offer_events
    unique_id = f"{log['transactionHash']}_{log['logIndex']}"
    
    # Get timestamp value
    timestamp_value = _get_timestamp_value(log)

    # Build the SQL query
    insert_query = """
        INSERT INTO offer_events (
            offer_id, event_type, buyer_address, amount_bought, price_bought,
            transaction_hash, block_number, log_index, unique_id,
            event_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    try:
        cursor.execute(
            insert_query,
            (
                log['offerId'],
                log['topic'],
                Web3.to_checksum_address(log['buyer']),
                str(log['amount']),
                str(log['price']),
                log['transactionHash'],
                log['blockNumber'],
                log['logIndex'],
                unique_id,
                timestamp_value
            )
        )
    except sqlite3.IntegrityError as e:
        # Ignore duplicate entries -> silently skip already-added entries
        if 'UNIQUE constraint failed: offer_events.unique_id' not in str(e):
            raise e
    
    # Get current offer status and update if necessary
    status = _get_offer_status(cursor, log['offerId'])
    if status is not None and status != 'InProgress':
        cursor.execute(
            "UPDATE offers SET status = ? WHERE offer_id = ?",
            (status, log['offerId'])
        )


def _handle_offer_updated(
    cursor: sqlite3.Cursor,
    log: Dict
) -> None:
    """
    Handle 'OfferUpdated' event by recording the update and setting status to 'InProgress'.
    
    Args:
        cursor: Database cursor
        log: Event log data
    """
    # Create a unique ID for the primary key of the table offer_events
    unique_id = f"{log['transactionHash']}_{log['logIndex']}"
    
    # Get timestamp value
    timestamp_value = _get_timestamp_value(log)

    # Build the SQL query
    insert_query = """
        INSERT INTO offer_events (
            offer_id, event_type, amount, price,
            transaction_hash, block_number, log_index, unique_id,
            event_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        cursor.execute(
            insert_query,
            (
                log['offerId'],
                log['topic'],
                str(log['newAmount']),
                str(log['newPrice']),
                log['transactionHash'],
                log['blockNumber'],
                log['logIndex'],
                unique_id,
                timestamp_value
            )
        )
    except sqlite3.IntegrityError as e:
        # Ignore duplicate entries -> silently skip already-added entries
        if 'UNIQUE constraint failed: offer_events.unique_id' not in str(e):
            raise e
    
    # Update offer status to 'InProgress'
    cursor.execute(
        "UPDATE offers SET status = 'InProgress' WHERE offer_id = ?",
        (log['offerId'],)
    )


def _handle_offer_deleted(
    cursor: sqlite3.Cursor,
    log: Dict
) -> None:
    """
    Handle 'OfferDeleted' event by recording the deletion and setting status to 'Deleted'.
    
    Args:
        cursor: Database cursor
        log: Event log data
    """
    # Create a unique ID for the primary key of the table offer_events
    unique_id = f"{log['transactionHash']}_{log['logIndex']}"
    
    # Get timestamp value
    timestamp_value = _get_timestamp_value(log)

    # Build the SQL query
    insert_query = """
        INSERT INTO offer_events (
            offer_id, event_type, transaction_hash, block_number, log_index, unique_id,
            event_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    try:
        cursor.execute(
            insert_query,
            (
                log['offerId'],
                log['topic'],
                log['transactionHash'],
                log['blockNumber'],
                log['logIndex'],
                unique_id,
                timestamp_value
            )
        )
    except sqlite3.IntegrityError as e:
        # Ignore duplicate entries -> silently skip already-added entries
        if 'UNIQUE constraint failed: offer_events.unique_id' not in str(e):
            raise e
    
    # Update offer status to 'Deleted'
    cursor.execute(
        "UPDATE offers SET status = 'Deleted' WHERE offer_id = ?",
        (log['offerId'],)
    )