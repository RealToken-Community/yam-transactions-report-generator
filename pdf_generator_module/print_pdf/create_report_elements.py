from pdf_generator_module.print_pdf.internals._utils import _get_report_parameter_section, _format_number, _format_timestamp, _aggregate_total_row
from pdf_generator_module.print_pdf.internals._style import _get_title_style, _get_user_addresses_style, _get_event_type_subtitle_style, _get_link_style, _get_header_style, _get_common_style, _get_buy_sell_table_style, _get_columns_width_buy_sell_table, _get_columns_width_exchange_table, _get_exchange_table_style
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import datetime
from typing import List

def create_report_elements(
        user_addresses: List[str],
        start_date: str,
        end_date: str,
        events_buyer: list,
        events_seller: list,
        blockchain_contracts: dict,
        realtokens: dict,
        transaction_type_to_display: List[str] = ['buy', 'sell', 'exchange'],
        display_tx_hash = True
        ):

    # Get the styling of the different section of the PDF
    title_style = _get_title_style()
    user_addresses_style = _get_user_addresses_style()
    event_type_subtitle_style = _get_event_type_subtitle_style()
    link_style = _get_link_style()
    header_style = _get_header_style()
    common_style = _get_common_style()
    buy_sell_style = _get_buy_sell_table_style()
    exchange_style = _get_exchange_table_style()

    # Make the title section
    title_section = Paragraph(f'YAM TRANSACTIONS REPORT', title_style)

    # Make the report parameter section (section where the dates are written)
    report_parameter = _get_report_parameter_section(start_date, end_date, user_addresses)
    report_parameter_section = Paragraph(f"{report_parameter}<br/>", user_addresses_style)

    # Make the user address(es) section (section where the user address(es) are written)
    user_addresses_section = Paragraph("<br/>".join(user_addresses), user_addresses_style)

    # Make the type event subtitle section
    buy_type_sub_title_section = Paragraph(f'<u>BUY Transactions</u>', event_type_subtitle_style)
    sell_type_sub_title_section = Paragraph(f'<u>SELL Transactions</u>', event_type_subtitle_style)
    exchange_type_sub_title_section = Paragraph(f'<u>EXCHANGE Transactions</u>', event_type_subtitle_style)


    # Header_table
    headers_table_buy_and_sell = ['Timestamp', 'Type', 'Realtoken name', 'Amount', 'Price/token', 'Payment token', 'Total price']
    headers_table_exchange = ['Timestamp', 'Type', 'Amount', 'Token bought', 'Amount', 'Token sold', 'Rate']

    # Add the Tx column only if it is desired by the user
    if display_tx_hash: 
        headers_table_buy_and_sell.append('Tx')
        headers_table_exchange.append('Tx')

    # columns width
    col_widths_buy_sell_table = _get_columns_width_buy_sell_table(display_tx_hash)
    col_widths_exchange_table = _get_columns_width_exchange_table(display_tx_hash)

    # list for all the transactions data
    buy_data_table = []
    sell_data_table = []
    exchange_data_table = []

    # A user can be either a buyer or a seller, and interact with either a sell offer or a purchase offer.
    # This results in four possible modes (exchanged not included) + 2 others modes for exchange:
    # 1. The user creates a sell offer          => they are SELLING realtokens.
    # 2. The user responds to a sell offer      => they are BUYING realtokens.
    # 3. The user creates a purchase offer      => they are BUYING realtokens.
    # 4. The user responds to a purchase offer  => they are SELLING realtokens.
    #
    # 5. The user exchange a payment token against another payment token (e.g. REUSD for USDC)
    # 6. The user exchange a realtoken against another realtoken
    # 
    # Depending on the mode, the event will be recorded in either the sell table or the buy table.

    for event in events_buyer + events_seller:

        if event['buyer_token'] in [contract["address"] for contract in blockchain_contracts.values()] and event['offer_token'] in [contract["address"] for contract in blockchain_contracts.values()]:
            mode = 5 # Exchange between two "payment token" (e.g. REUSD swapped to USDC) 

        elif event['buyer_token'] in realtokens.keys() and event['offer_token'] in realtokens.keys():
            mode = 6 # Exchange between two Realtokens

        elif event['buyer_token'] in [contract["address"] for contract in blockchain_contracts.values()] and event['seller_address'] in user_addresses:
            mode = 1 # The user has created a sell offer  -> they are SELLING realtokens.
        
        elif event['buyer_token'] in [contract["address"] for contract in blockchain_contracts.values()] and event['buyer_address'] in user_addresses:
            mode = 2 # The user has responded a sell offer  -> they are BUYING realtokens.

        elif event['offer_token'] in [contract["address"] for contract in blockchain_contracts.values()] and event['seller_address'] in user_addresses:
            mode = 3 # The user has created a purchase offer  -> they are BUYING realtokens.
        
        elif event['offer_token'] in [contract["address"] for contract in blockchain_contracts.values()] and event['buyer_address'] in user_addresses:
            mode = 4 # The user has responded a purchase offer -> they are SELLING realtokens.

        else: continue

        realtoken_decimals = 18

        price_unit256 = int(event['price_bought'])
        amount_unit256 = int(event['amount_bought'])

        if mode in [1, 2]: # Sell offer
            if event['offer_token'] == '0x0675e8F4A52eA6c845CB6427Af03616a2af42170': realtoken_decimals = 9 # RWA has 9 decimals and not 18
            realtoken_name = realtokens.get(event['offer_token'], {}).get('shortName', 'Unknown realtoken')
            try:
                payment_token_name = next(key for key, contract in blockchain_contracts.items() if contract["address"] == event['buyer_token'])
                payment_token_decimals = blockchain_contracts[payment_token_name]['decimals']
            except StopIteration:
                payment_token_name = "Unknown token"
                payment_token_decimals = 18

            price_per_token = price_unit256 / 10 ** payment_token_decimals # convert price unit256 into dec
            amount = amount_unit256 / 10 ** realtoken_decimals # convert amount unit256 into dec
            total_price = price_per_token * amount
        
        elif mode in [3, 4]: # Purchase offer
            if event['buyer_token'] == '0x0675e8F4A52eA6c845CB6427Af03616a2af42170': realtoken_decimals = 9 # RWA has 9 decimals and not 18
            realtoken_name = realtokens.get(event['buyer_token'], {}).get('shortName', 'Unknown realtoken')
            try:
                payment_token_name = next(key for key, contract in blockchain_contracts.items() if contract["address"] == event['offer_token'])
                payment_token_decimals = blockchain_contracts[payment_token_name]['decimals']
            except StopIteration:
                payment_token_name = "Unknown token"
                payment_token_decimals = 18
            
            price_per_token = 10 ** realtoken_decimals / price_unit256 # convert price unit256 into dec
            amount = amount_unit256 * price_unit256 /  10 ** (payment_token_decimals + realtoken_decimals) # convert amount unit256 into dec
            total_price = price_per_token * amount

        # Populate the row
        row = []

        # Timestamp
        row.append(_format_timestamp(event['event_timestamp']))

        # Type
        if mode in [1, 4]: # User is SELLING realtokens
            row.append('Sell')
        elif mode in [2, 3]: # User is BUYING realtokens
            row.append('Buy')
        elif mode in [5, 6]: # User is EXCHANGING tokens
            row.append('Exchange')

        # Realtoken Name
        if mode in [1, 2, 3, 4]:
            row.append(realtoken_name)

        # Amount
        if mode in [1, 2, 3, 4]:
            row.append(_format_number(amount))

        # Price per unit
        if mode in [1, 2, 3, 4]:
            row.append(_format_number(price_per_token))
        
        # Payment token
        if mode in [1, 2, 3, 4]:
            row.append(payment_token_name)
        
        # Total price
        if mode in [1, 2, 3, 4]:
            row.append(_format_number(total_price))

        # link to tx
        if mode in [1, 2, 3, 4] and display_tx_hash:
            link_paragraph = Paragraph(f'<link href="https://gnosisscan.io/tx/{event["transaction_hash"]}">URL</link>', link_style)
            row.append(link_paragraph)

        if mode in [1, 4]: # User is SELLING realtokens
            sell_data_table.append(row)
        elif mode in [2, 3]: # User is BUYING realtokens
            buy_data_table.append(row)

        if mode in [5, 6]:
            if event['buyer_address'] in user_addresses:
                token_bought_address = event['offer_token']
                token_sold_address = event['buyer_token']
            elif event['seller_address'] in user_addresses:
                token_bought_address = event['buyer_token']
                token_sold_address = event['offer_token']
            
            price_unit256 = int(event['price_bought'])
            amount_unit256 = int(event['amount_bought'])
        
        if mode == 5:
            token_bought_name = next(key for key, contract in blockchain_contracts.items() if contract["address"] == token_bought_address)
            token_bought_decimals = blockchain_contracts[token_bought_name]['decimals']
            token_sold_name = next(key for key, contract in blockchain_contracts.items() if contract["address"] == token_sold_address)
            token_sold_decimals = blockchain_contracts[token_sold_name]['decimals']
        
        elif mode == 6:
            token_bought_decimals = token_sold_decimals = 18
            if token_bought_address == '0x0675e8F4A52eA6c845CB6427Af03616a2af42170': token_bought_decimals = 9 # RWA has 9 decimals and not 18
            if token_sold_address == '0x0675e8F4A52eA6c845CB6427Af03616a2af42170': token_sold_decimals = 9 # RWA has 9 decimals and not 18
            token_bought_name = realtokens.get(token_bought_address, {}).get('shortName', 'Unknown realtoken')
            token_sold_name = realtokens.get(token_sold_address, {}).get('shortName', 'Unknown realtoken')

        if mode in [5, 6]:

            if event['buyer_address'] in user_addresses:
                amount_token_bought = amount_unit256 / 10 ** token_bought_decimals
                exchange_rate = price_unit256 / 10 ** token_sold_decimals
                amount_token_sold = amount_token_bought * exchange_rate
            elif event['seller_address'] in user_addresses:
                amount_token_bought = amount_unit256 / 10 ** token_sold_decimals
                exchange_rate = price_unit256 / 10 ** token_bought_decimals
                amount_token_sold = amount_token_bought * exchange_rate

            # Amount token bought
            row.append(_format_number(amount_token_bought))

            # Token bought
            row.append(token_bought_name)

            # Amount token sold
            row.append(_format_number(amount_token_sold))

            # Token sold
            row.append(token_sold_name)

            # Exchange rate
            row.append(_format_number(exchange_rate))

            # link to tx
            if display_tx_hash:
                link_paragraph = Paragraph(f'<link href="https://gnosisscan.io/tx/{event["transaction_hash"]}">URL</link>', link_style)
                row.append(link_paragraph)

            exchange_data_table.append(row)

   
    # sort the transaction from oldest to newest
    sell_data_table.sort(key=lambda row: datetime.strptime(row[0], "%d %b %Y %Hh%M"))
    buy_data_table.sort(key=lambda row: datetime.strptime(row[0], "%d %b %Y %Hh%M"))
    exchange_data_table.sort(key=lambda row: datetime.strptime(row[0], "%d %b %Y %Hh%M"))
    
    # calcul the total (sum) of every buy transaction and every sell transaction
    total_sell, total_buy = _aggregate_total_row(sell_data_table, buy_data_table)

    # if a string is too long for the width of the column, its font size is decreased
    # List to track which cells need the smaller font size
    small_font_cells_buy_table = []
    small_font_cells_sell_table = []
    small_font_cells_exchange_table = []
    
    # in the payment column, ARMMV3WXDAI and ARMMV3USDC are too long for the column width
    for i, item in enumerate(buy_data_table):
        if item[5] in ['ARMMV3WXDAI', 'ARMMV3USDC']:
            small_font_cells_buy_table.append((5, i+1))
    for i, item in enumerate(sell_data_table):
        if item[5] in ['ARMMV3WXDAI', 'ARMMV3USDC']:
            small_font_cells_sell_table.append((5, i+1))

    # for exchanges, when token names that are too long, font size is decreased
    for i, item in enumerate(exchange_data_table):
        if len(item[3]) > 24:
            small_font_cells_exchange_table.append((3, i+1))
        if len(item[5]) > 24:
            small_font_cells_exchange_table.append((5, i+1))
    

    buy_table = Table([headers_table_buy_and_sell] + buy_data_table + [total_buy], colWidths=col_widths_buy_sell_table)
    sell_table =  Table([headers_table_buy_and_sell] + sell_data_table + [total_sell], colWidths=col_widths_buy_sell_table)
    exchange_table = Table([headers_table_exchange] + exchange_data_table, colWidths=col_widths_exchange_table)
    
    buy_table_style = []
    sell_table_style = []
    
    # Add special styling for the small font cells
    for col, row in small_font_cells_buy_table:
        buy_table_style += [
            ("FONTSIZE", (col, row), (col, row), 6.75),
            ("TOPPADDING", (col, row), (col, row), 3),
        ]
    for col, row in small_font_cells_sell_table:
        sell_table_style+= [
            ("FONTSIZE", (col, row), (col, row), 6.75),
            ("TOPPADDING", (col, row), (col, row), 3),
        ]
    for col, row in small_font_cells_exchange_table:
        exchange_style+= [
            ("FONTSIZE", (col, row), (col, row), 6),
            ("TOPPADDING", (col, row), (col, row), 7),
        ]

    buy_table.setStyle(TableStyle(common_style + header_style + buy_sell_style + buy_table_style))
    sell_table.setStyle(TableStyle(common_style + header_style + buy_sell_style + sell_table_style))
    exchange_table.setStyle(TableStyle(common_style + header_style + exchange_style))

    elements = []
    elements.append(title_section)
    elements.append(report_parameter_section)
    elements.append(user_addresses_section)
    elements.append(Spacer(1, 0.2 * cm))
    if 'buy' in transaction_type_to_display:
        
        elements.append(buy_type_sub_title_section)
        elements.append(Spacer(1, 0.2 * cm))
        
        if len(buy_data_table) > 0: # if table is not empty (we make sure they are transactions for the period of time given by the user):
            elements.append(buy_table)
        else:
            elements.append(Paragraph("No buy transaction for this period of time", user_addresses_style))
        elements.append(PageBreak())
    
    if 'sell' in transaction_type_to_display:
        elements.append(sell_type_sub_title_section)
        elements.append(Spacer(1, 0.2 * cm))
        
        if len(sell_data_table) > 0: # if table is not empty (we make sure they are transactions for the period of time given by the user):
            elements.append(sell_table)
        else:
            elements.append(Paragraph("No sell transaction for this period of time", user_addresses_style))
        elements.append(PageBreak())

    if 'exchange' in transaction_type_to_display:
        elements.append(exchange_type_sub_title_section)
        elements.append(Spacer(1, 0.2 * cm))
        
        if len(exchange_data_table) > 0: # if table is not empty (we make sure they are transactions for the period of time given by the user):
            elements.append(exchange_table)
        else:
            elements.append(Paragraph("No exchange transaction for this period of time", user_addresses_style))

    return elements