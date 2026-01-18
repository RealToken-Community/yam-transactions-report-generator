from typing import List, Dict, Optional, Any
import sqlite3

def _get_offer_status(cursor: sqlite3.Cursor, offer_id: str) -> Optional[str]:
    """
    Calculate the current status of an offer based on its event history.
    
    Determines offer status using the following logic:
    - If the last event is 'OfferDeleted', status is 'Deleted'
    - Otherwise, calculate remaining amount starting from the latest 'OfferUpdated' event (or from the original offer if no updates)
    - If remaining amount is 0, status is 'SoldOut'
    - If remaining amount is > 0, status is 'InProgress'
    
    Args:
        cursor: Database cursor
        offer_id: ID of the offer to check
        
    Returns:
        Current status ('Deleted', 'SoldOut', 'InProgress') or None if status cannot be determined
    """
    # Get all events for this offer
    events = _get_all_events_from_offer_id(cursor, offer_id)
    
    # Check if offer was deleted (last event is OfferDeleted)
    if len(events) > 0 and events[-1].get('event_type') == 'OfferDeleted':
        return 'Deleted'
    
    # Find the most recent 'OfferUpdated' event
    last_offer_updated_index = None
    
    for i, event in enumerate(events):
        if event.get('event_type') == 'OfferUpdated':
            # Keep track of the index of the last 'OfferUpdated' event
            last_offer_updated_index = i
    
    # If an 'OfferUpdated' event was found, consider only events after that one
    if last_offer_updated_index is not None:
        events = events[last_offer_updated_index:]
    
    # Calculate remaining amount
    if len(events) > 0:
        # Get initial amount from first event (either original or after last update)
        initial_amount = events[0].get('initial_amount', events[0].get('amount'))
        
        # Ensure we have a valid amount to start with
        if initial_amount is None:
            return None
            
        amount = int(initial_amount)
        
        # Subtract all bought amounts from subsequent acceptance events
        for event in events[1:]:
            amount_bought = event.get('amount_bought')
            if amount_bought is not None:
                amount -= int(amount_bought)
    else:
        return None
    
    # Determine status based on remaining amount
    if amount == 0:
        return 'SoldOut'
    elif amount > 0:
        return 'InProgress'
    else:
        # Negative amount is an error condition
        return None
    

def _get_all_events_from_offer_id(cursor: sqlite3.Cursor, offer_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all events related to a specific offer.
    
    Fetches the original offer and all events from the database, combines them
    into a single list, and sorts them by block number and log index to maintain
    chronological order.
    
    Args:
        cursor: Database cursor
        offer_id: ID of the offer to fetch events for
        
    Returns:
        List of dictionaries containing event data, sorted by block order
    """
    result = []
    
    # Query to get the offer from the offers table
    cursor.execute("SELECT * FROM offers WHERE offer_id = ?", (offer_id,))
    offer = cursor.fetchone()
    
    # If the offer exists, add it to the result list
    if offer:
        # Convert the tuple to a dictionary using column names
        offer_dict = dict(zip([column[0] for column in cursor.description], offer))
        result.append(offer_dict)
        
        # Query to get all events related to this offer from offer_events table
        cursor.execute(
            "SELECT * FROM offer_events WHERE offer_id = ? ORDER BY event_timestamp ASC", 
            (offer_id,)
        )
        events = cursor.fetchall()
        
        # Add each event to the result list
        for event in events:
            # Convert the tuple to a dictionary using column names
            event_dict = dict(zip([column[0] for column in cursor.description], event))
            result.append(event_dict)
        
        # Sort all entries by blockchain order (block number and log index)
        result = sorted(result, key=lambda event: (event['block_number'], event['log_index']))
    
    return result