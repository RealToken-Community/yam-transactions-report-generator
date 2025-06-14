import sqlite3
from typing import List, Dict, Union
from datetime import datetime

def get_accepted_offers_by_buyer_datetime(
    db_path: str, 
    buyer_addresses: Union[str, List[str]], 
    from_datetime: Union[str, datetime], 
    to_datetime: Union[str, datetime]
) -> List[Dict[str, any]]:
    """
    Retrieve accepted offers for specific buyer addresses within a datetime range.

    Args:
        db_path (str): Path to the SQLite database.
        buyer_addresses (Union[str, List[str]]): Single buyer address or list of buyer addresses.
        from_datetime (Union[str, datetime]): Starting datetime (ISO format string or datetime object).
        to_datetime (Union[str, datetime]): Ending datetime (ISO format string or datetime object).

    Returns:
        List[Dict[str, any]]: List of dictionaries with event data.
    """
    conn = sqlite3.connect(db_path)
    
    try:
        cursor = conn.cursor()
        
        # Convert single address to list if necessary
        if isinstance(buyer_addresses, str):
            buyer_addresses = [buyer_addresses]
        
        # Convert datetime objects to strings if necessary
        if isinstance(from_datetime, datetime):
            from_datetime = from_datetime.isoformat()
        if isinstance(to_datetime, datetime):
            to_datetime = to_datetime.isoformat()
        
        # Construct placeholders for the SQL IN clause
        placeholders = ', '.join(['?' for _ in buyer_addresses])
        
        query = f"""
        SELECT 
            offer_events.offer_id,
            offer_events.event_type,
            offer_events.buyer_address,
            offer_events.amount_bought,
            offer_events.block_number,
            offer_events.transaction_hash,
            offer_events.price_bought,
            offer_events.event_timestamp,
            offers.offer_token,
            offers.buyer_token,
            offers.seller_address
        FROM offer_events
        JOIN offers ON offer_events.offer_id = offers.offer_id
        WHERE offer_events.event_type = 'OfferAccepted'
        AND offer_events.buyer_address IN ({placeholders})
        AND offer_events.event_timestamp BETWEEN ? AND ?
        ORDER BY offer_events.event_timestamp ASC
        """
        
        parameters = buyer_addresses + [from_datetime, to_datetime]
        cursor.execute(query, parameters)
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    finally:
        conn.close()
