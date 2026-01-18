from datetime import datetime
from typing import List

def _get_report_parameter_section(start_date:str, end_date: str, user_addresses: List[str]):

    # Format user addresses text based on number of addresses
    report_parameter = f"All YAM transactions between {start_date} and {end_date} for the following wallet "
    
    if len(user_addresses) == 1:
        report_parameter += "address:"
    else:
        report_parameter += "addresses:"
    
    return report_parameter

def _format_number(value, threshold=0.01):
    return f"{value:.2f}" if value >= threshold else "< 0.01"

def _format_timestamp(raw_timestamp):
    return datetime.strptime(raw_timestamp[:-3], '%Y-%m-%d %H:%M').strftime('%d %b %Y %Hh%M').lstrip('0')

def _aggregate_total_row(sell_data_table, buy_data_table):

    total_buy = ["Total", "", "", 0.0, "", "", 0.0, ""]
    total_sell = ["Total", "", "", 0.0, "", "", 0.0, ""]

    for row in sell_data_table:
        try:
            total_sell[3] += float(row[3])
        except ValueError:
            pass
        try:
            total_sell[6] += float(row[6])
        except ValueError:
            pass
    
    for row in buy_data_table:
        try:
            total_buy[3] += float(row[3])
        except ValueError:
            pass
        try:
            total_buy[6] += float(row[6])
        except ValueError:
            pass
    
    total_sell[3] = _format_number(total_sell[3])
    total_sell[6] = _format_number(total_sell[6])
    
    total_buy[3] = _format_number(total_buy[3])
    total_buy[6] = _format_number(total_buy[6])
    
    return total_sell, total_buy