import json
import sqlite3
from yam_indexing_module.the_graphe_handler.internals import fetch_all_offer_created, fetch_all_offer_deleted, fetch_all_offer_updated, fetch_all_offer_accepted
from yam_indexing_module.db_operations import add_events_to_db, init_db


def initialize_indexing_module():
    with open('config.json', 'r') as config_file:
            config = json.load(config_file)

    API_KEY = config["the_graph_api_key"]
    DB_PATH = config["db_path"]
    SUBGRAPH_URL = config['subgraph_url']

    # initialize DB
    init_db(DB_PATH)

    # Fetch from TheGraph all offerCreated and add them to the DB
    print("\nofferCreated:")
    created_offers = fetch_all_offer_created(API_KEY, SUBGRAPH_URL)
    add_events_to_db(DB_PATH, None, None, created_offers, True)

    # Fetch from TheGraph all offerAccepted/offerDeleted/offerUpdated and add them to the DB
    print("\n\nofferAccepted, offerUpdated and offerDeleted:")
    accepted_offers = fetch_all_offer_accepted(API_KEY, SUBGRAPH_URL)
    updated_offers = fetch_all_offer_updated(API_KEY, SUBGRAPH_URL)
    deleted_offers = fetch_all_offer_deleted(API_KEY, SUBGRAPH_URL)
    all_events = accepted_offers + updated_offers + deleted_offers
    all_events_sorted = sorted(all_events, key=lambda x: x['timestamp'])
    add_events_to_db(DB_PATH, None, None, all_events_sorted, True)

    highest_block_number = max(created_offers[-1]['blockNumber'], all_events_sorted[-1]['blockNumber'])
    
    # Add indexing state record

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO indexing_state (from_block, to_block) 
        VALUES (?, ?)
    """, (25530394, highest_block_number))
    conn.commit()
    conn.close()

    print(f'\nInitialization completed! DB indexed up to block {highest_block_number}')


if __name__ == "__main__":
    initialize_indexing_module()