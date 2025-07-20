import json
import sqlite3
import logging
import time
from web3 import Web3
from pprint import pprint
from yam_indexing_module.the_graphe_handler import backfill_db_block_range
from yam_indexing_module.db_operations.internal._db_operations import _get_last_indexed_block
from yam_indexing_module.logs_handlers.get_and_decode_logs_yam import get_raw_logs_yam, decode_raw_logs_yam
from yam_indexing_module.db_operations import add_events_to_db
from yam_indexing_module.logging.logging_config import setup_logging


BLOCK_TO_RETRIEVE = 3                   # Number of block to retrieve from the W3 RPC by HTTP request 
COUNT_BEFORE_RESYNC = 100               # Number of retrieve before resynchronizing to the latest block
BLOCK_BUFFER = 5                        # Gap between the latest block available and what is actually retrieve
TIME_TO_WAIT_BEFORE_RETRY = 1.5         # time to wait before retry when RPC is not available
MAX_RETRIES_PER_BLOCK_RANGE = 6         # Number of time the request will be retried when it has failed before changing the RPC
COUNT_PERIODIC_BACKFILL_THEGRAPH = 960  # Number of iteration before backfilling the blocks into the DB the blocks of the last few hours (with TheGraph)


def main_indexing():

    #### LOAD DATA ####

    # Set up logging at the start of your application
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    with open('Ressources/blockchain_contracts.json', 'r') as f:
        yam_contract_address = json.load(f)['contracts']['yamv1']['address']

    # Load the config file
    with open("config.json", "r") as f:
        config = json.load(f)
    w3_urls = config["w3_urls"]
    db_path = config['db_path']
    subgraph_url = config['subgraph_url']
    the_graph_api_key = config['the_graph_api_key']

    #### INITIALIZATION ####

    w3_indice = 0
    w3 = Web3(Web3.HTTPProvider(w3_urls[w3_indice]))

    last_block_indexed = _get_last_indexed_block(db_path)
    latest_block_number = w3.eth.block_number

    # backfill DB from the last indexed block in DB to the latest available block in the blockchain
    backfill_db_block_range(db_path, subgraph_url, the_graph_api_key, last_block_indexed, latest_block_number)

    from_block = latest_block_number - BLOCK_BUFFER - BLOCK_TO_RETRIEVE + 1
    to_block = latest_block_number - BLOCK_BUFFER
    sync_counter = 0
    backfill_thegraph_count = 0

    print('indexing module running...')

    #### INDEXING LOGIC ####

    try:
        while True:
        
            start_time = time.time()

            success = False
        
            for attempt in range(MAX_RETRIES_PER_BLOCK_RANGE):
            
                try:
                    raw_logs = get_raw_logs_yam(w3, yam_contract_address, from_block, to_block)
                    success = True
                    break # leave the for loop if success
                
                except Exception as e:
                    
                    if attempt < MAX_RETRIES_PER_BLOCK_RANGE - 1:
                        logger.info(f"Blocks retrieval failed. Retrying in {TIME_TO_WAIT_BEFORE_RETRY} seconds...")
                        time.sleep(TIME_TO_WAIT_BEFORE_RETRY)
                    
                    else:
                        # if the request has fails severals time, change RPC
                        old_indice = w3_indice
                        w3_indice = (w3_indice + 1) % len(w3_urls) # This will give you the sequence: 0 → 1 → 2 → ... → n → 0 → 1 → 2 → ... → n → 0 ...
                        w3 = Web3(Web3.HTTPProvider(w3_urls[w3_indice]))
                        logger.info(f"Blocks retrieval failed too many times. Changing from w3 RPC n°{old_indice + 1} to w3 RPC n°{w3_indice + 1} [{w3.provider.endpoint_uri.split('//')[1].rsplit('/', 1)[0]}]")
                        continue
            
            if not success:
                logger.info(f"All attempts with the same RPC [{w3.provider.endpoint_uri.split('//')[1].rsplit('/', 1)[0]}] failed.")
                continue
            
            decoded_logs = decode_raw_logs_yam(raw_logs)
        
            ### Add logs to the DB
            add_events_to_db(db_path, from_block, to_block, decoded_logs)
            logger.info(f"{len(decoded_logs)} YAM log(s) retrieved from block {from_block} to {to_block}")
        
            from_block = to_block + 1
            to_block += BLOCK_TO_RETRIEVE
        
            sync_counter += 1
            backfill_thegraph_count += 1
        
            if sync_counter > COUNT_BEFORE_RESYNC:
                sync_counter = 0
                latest_block_number = w3.eth.block_number
                # we resynchronize the 'to_block' to the latest block without touching the 'from_block'
                to_block = latest_block_number - BLOCK_BUFFER
                
                # We calcul the deviation and we move back the 'from_block' if it is ahead of what it should do
                deviation = to_block - from_block - BLOCK_TO_RETRIEVE
                if deviation < 0:
                    from_block = latest_block_number - BLOCK_BUFFER - BLOCK_TO_RETRIEVE + 1
                logger.info(f"resync on newest block - deviation was {deviation} block(s)")

            if backfill_thegraph_count > COUNT_PERIODIC_BACKFILL_THEGRAPH:
                backfill_thegraph_count = 0
                # backfill DB from the last indexed block in DB to the latest available block in the blockchain
                from_block_backfill = to_block - 17280 # 17280 blocks = 1 day
                backfill_db_block_range(db_path, subgraph_url, the_graph_api_key, from_block_backfill, to_block)
            
            # Adjust sleep time accordingly - we don't want to deviate so we take the execution time into account
            execution_time = time.time() - start_time
            time_to_sleep = max(0, BLOCK_TO_RETRIEVE * 5.1 - execution_time) # 5.1 because it seems to go too fast with 5 and it ends up fetching block that doesn't exist yet
            
            # Sleep for the adjusted time
            time.sleep(time_to_sleep)

    except KeyboardInterrupt:
        logger.info("Received Ctrl+C, shutting down the indexing service...")
        print("Process stopped by user")
        raise
    except Exception as e:
        logger.error(f"Indexing loop failed with error: {str(e)}", exc_info=True)
        print(f"Indexing loop failed with error: {str(e)}")

if __name__ == "__main__":
    while True:
        try:
            main_indexing()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception("Fatal error in main_indexing. Restarting in 30 seconds...")
            time.sleep(30)