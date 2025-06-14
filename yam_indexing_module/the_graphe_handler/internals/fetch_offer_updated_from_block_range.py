import requests
from typing import List, Dict, Any, Optional
import time
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

def fetch_offer_updated_from_block_range(
    subgraph_url: str, 
    api_key: str, 
    from_block: int, 
    to_block: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Fetch all OfferUpdated entities from a range of blocks.
    
    Args:
        subgraph_url (str): The Graph subgraph endpoint URL
        api_key (str): The Graph API key for authentication
        from_block (int): The starting block number (inclusive)
        to_block (Optional[int]): The ending block number (inclusive). If None, fetches to latest block
        
    Returns:
        List[Dict[str, Any]]: List of all OfferUpdated entities from the specified block range
    """
    
    all_entities = []
    last_id = ""
    page_size = 1000  # Maximum allowed by The Graph
    
    while True:
        # Build the GraphQL query using blockNumber_gte and blockNumber_lte for range
        if to_block is not None:
            block_filter = f'blockNumber_gte: {from_block}, blockNumber_lte: {to_block}'
        else:
            block_filter = f'blockNumber_gte: {from_block}'
        
        # Build the where clause with pagination
        if last_id:
            where_clause = f'where: {{{block_filter}, id_gt: "{last_id}"}}'
        else:
            where_clause = f'where: {{{block_filter}}}'
        
        query = f"""
        {{
          offerUpdateds(
            first: {page_size},
            {where_clause},
            orderBy: id,
            orderDirection: asc
          ) {{
            id
            offerId
            oldPrice
            oldAmount
            newPrice
            newAmount
            transactionHash
            logIndex
            blockNumber
            timestamp
          }}
        }}
        """
        
        # Prepare the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            'query': query
        }
        
        try:
            # Make the request
            response = requests.post(subgraph_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if 'errors' in data:
                error_msg = f"GraphQL errors: {data['errors']}"
                logger.error(error_msg)
                return []
            
            # Extract the entities
            entities = data.get('data', {}).get('offerUpdateds', [])
            
            if not entities:
                # No more entities to fetch
                break
            
            # Add entities to our collection
            all_entities.extend(entities)
            
            # Update last_id for next iteration
            last_id = entities[-1]['id']
            
            # If we got fewer entities than page_size, we've reached the end
            if len(entities) < page_size:
                break
                
            # Small delay to be respectful to the API
            time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP request failed: {e}"
            logger.error(error_msg)
            return []
        except Exception as e:
            error_msg = f"Failed to fetch entities: {e}"
            logger.error(error_msg)
            return []
    
    # Add topic to all entities
    for i, entity in enumerate(all_entities):
        all_entities[i]['topic'] = 'OfferUpdated'
    
    return all_entities