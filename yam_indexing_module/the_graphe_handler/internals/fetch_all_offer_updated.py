import requests
import json
from typing import List, Dict, Any

def fetch_all_offer_updated(api_key: str, url: str) -> List[Dict[str, Any]]:
    """
    Fetch all offerUpdated entities from The Graph subgraph with cursor-based pagination.
    
    Arg:
        api_key (str): The Graph API key for authentication
        url (str): The subgraph url to query
    
    Returns:
        List[Dict[str, Any]]: Complete list of all offerUpdated entities
    
    Raises:
        requests.RequestException: If API request fails
        ValueError: If response format is unexpected
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    all_offers = []
    batch_size = 1000
    last_id = ""  # For cursor-based pagination
    
    # GraphQL query using cursor-based pagination (where clause)
    query_template = """
    query GetOfferUpdated($first: Int!, $lastId: String!) {
        offerUpdateds(
            first: $first,
            where: { id_gt: $lastId },
            orderBy: id,
            orderDirection: asc
        ) {
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
        }
    }
    """
    
    while True:
        # Prepare the GraphQL request
        payload = {
            "query": query_template,
            "variables": {
                "first": batch_size,
                "lastId": last_id
            }
        }
         
        # Make the request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Check for GraphQL errors
        if "errors" in data:
            raise ValueError(f"GraphQL errors: {data['errors']}")
        
        # Extract the offers from this batch
        offers_batch = data.get("data", {}).get("offerUpdateds", [])
        
        if not offers_batch:
            break
        
        # Add to our complete list
        all_offers.extend(offers_batch)

        # Update progress counter (overwrite previous number)
        print(f"\rFetched {len(all_offers)} events offerUpdated from TheGraph...", end="", flush=True)
        
        # Update the cursor (last ID) for next batch
        last_id = offers_batch[-1]["id"]
        
        # If we got less than the batch size, we've reached the end
        if len(offers_batch) < batch_size:
            break
    
    for i, offer in enumerate(all_offers):
        all_offers[i]['topic'] = 'OfferUpdated'

    return all_offers