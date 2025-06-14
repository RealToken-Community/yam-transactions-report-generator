from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors 

def _get_title_style():
    title_style = ParagraphStyle(
        "TitleStyle",
        fontName="Helvetica-Bold",
        fontSize=20,
        alignment=1,
        spaceAfter=28,
        textColor=colors.black
    )
    return title_style

def _get_user_addresses_style():
    user_addresses_style = ParagraphStyle(
        "UserAddressesStyle",
        fontName="Helvetica",
        fontSize=9,
        alignment=0,
        spaceAfter=5,
        textColor=colors.black,
        leading=14
    )
    return user_addresses_style

def _get_event_type_subtitle_style():
    event_type_subtitle_style = ParagraphStyle(
        "EventTypeSubtitleStyle",
        fontName="Helvetica-Bold",
        fontSize=11,
        alignment=0,
        spaceAfter=5,
        textColor=colors.black,
    )
    return event_type_subtitle_style

def _get_link_style():
    link_style = ParagraphStyle(
       name="LinkStyle",
       fontSize=7,
    )
    return link_style

def _get_common_style():
    common_style = [
        ("GRID", (0, 0), (-1, -2), 0.5, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 9),  # Default font size
        ]
    return common_style

def _get_header_style():
    header_style = [

        # Headers
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#c79b22")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    return header_style


def _get_buy_sell_table_style():
    table_buy_sell_style = [

        # Amount header cell
        ("FONTSIZE", (3, 0), (4, 0), 7),
        ("TOPPADDING", (3, 0), (4, 0), 1),
        ("BOTTOMPADDING", (3, 0), (4, 0), 1),
        ("VALIGN", (3, 0), (4, 0), "BOTTOM"),

        # Payment token header cell
        ("FONTSIZE", (5, 0), (5, 0), 7),
        ("TOPPADDING", (5, 0), (5, 0), 1),
        ("BOTTOMPADDING", (5, 0), (5, 0), 1),
        ("VALIGN", (5, 0), (5, 0), "BOTTOM"),


        # Payment token column
        ("TOPPADDING", (5, 1), (5, -1), 0.25),
        ("BOTTOMPADDING", (5, 1), (5, -1), 0),
        ("VALIGN", (5, 1), (5, -1), "MIDDLE"),

        # Realtoken Name column
        ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"),

        # Total price column
        ("FONTNAME", (6, 1), (6, -1), "Helvetica-Bold"),

        # tx URL column
        ("FONTSIZE", (7, 1), (7, -1), 7),
        ("TOPPADDING", (7, 1), (7, -1), 1),
        ("BOTTOMPADDING", (7, 1), (7, -1), 1),

        # total row
        ("FONTSIZE", (0, -1), (-1, -1), 10),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F1E6C6")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BOX", (0, -1), (-1, -1), 0.5, colors.black),
        ]
    return table_buy_sell_style

def _get_exchange_table_style():
    table_exchange_style = [

        # Amount token bought header cell
        ("FONTSIZE", (2, 0), (2, 0), 7.5),
        ("TOPPADDING", (2, 0), (2, 0), 1),
        ("BOTTOMPADDING", (2, 0), (2, 0), 1),
        ("VALIGN", (2, 0), (2, 0), "BOTTOM"),
        # Amount token sold header cell
        ("FONTSIZE", (4, 0), (4, 0), 7.5),
        ("TOPPADDING", (4, 0), (4, 0), 1),
        ("BOTTOMPADDING", (4, 0), (4, 0), 1),
        ("VALIGN", (4, 0), (4, 0), "BOTTOM"),

        # transaction type column (Exchange)
        ("FONTSIZE", (1, 1), (1, -1), 7.5),
        ("BOTTOMPADDING", (1, 1), (1, -1), 2),

        # Realtoken/payment token Name column
        ("FONTNAME", (3, 1), (3, -1), "Helvetica-Bold"),
        ("FONTNAME", (5, 1), (5, -1), "Helvetica-Bold"),

        # tx URL column
        ("FONTSIZE", (7, 1), (7, -1), 7),
        ("TOPPADDING", (7, 1), (7, -1), 1),
        ("BOTTOMPADDING", (7, 1), (7, -1), 1),

        # Grid for last rwo (no total row on exchange)
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]
    return table_exchange_style


def _get_columns_width_buy_sell_table(display_tx_hash):
    
    # Column width
    TABLE_TOTAL_WIDTH = 520
    
    # The total percentages of each column should add up to 100%
    TX_COLUMN_SIZE = 5
    col_width_percentages = [
        18,                                                 # fixed
        7,                                                  # fixed
        (31 if display_tx_hash else (31 + TX_COLUMN_SIZE)), # adjusts column width
        7,                                                  # fixed
        9,                                                  # fixed
        12,                                                 # fixed
        11,                                                 # fixed
        (TX_COLUMN_SIZE if display_tx_hash else 0)          # adjusts column width
        ]
    assert sum(col_width_percentages) == 100, "Column widths must add up to 100%"

    # Convert percentages to actual widths
    col_widths = [TABLE_TOTAL_WIDTH * (p / 100) for p in col_width_percentages]

    return col_widths


def _get_columns_width_exchange_table(display_tx_hash):
    
    # Column width
    TABLE_TOTAL_WIDTH = 520
    
    # The total percentages of each column should add up to 100%
    TX_COLUMN_SIZE = 5
    col_width_percentages = [
        18,                                                     # fixed
        9,                                                      # fixed
        8,                                                      # fixed
        (23 if display_tx_hash else (23 + TX_COLUMN_SIZE/2)),   # adjusts column width
        8,                                                      # fixed
        (23 if display_tx_hash else (23 + TX_COLUMN_SIZE/2)),   # adjusts column width
        6,                                                      # fixed
        (TX_COLUMN_SIZE if display_tx_hash else 0)              # adjusts column width
        ]
    assert sum(col_width_percentages) == 100, "Column widths must add up to 100%"

    # Convert percentages to actual widths
    col_widths = [TABLE_TOTAL_WIDTH * (p / 100) for p in col_width_percentages]

    return col_widths

