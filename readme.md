# YAM Transactions Report Generator

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
  - [Step 1 – Configure config.json](#step-1--configure-configjson)
  - [Step 2 – Install Python Dependencies](#step-2--install-python-dependencies)
  - [Step 3 – Install Frontend Dependencies](#step-3--install-frontend-dependencies)
  - [Step 4 – Initialize the Indexing Module](#step-4--initialize-the-indexing-module)
- [Running the Project](#running-the-project)
  - [Start the Indexing Service](#start-the-indexing-service)
  - [Start the API Server](#start-the-api-server)
  - [Start the Web Interface](#start-the-web-interface)
- [Technical Analysis and Module Details](#technical-analysis-and-module-details)
  - [Indexing Module (Python)](#indexing-module-python)
  - [API & PDF Generation Module (Python)](#api--pdf-generation-module-python)
    - [Endpoints](#endpoints)
      - [`/health` – Health Check](#health--health-check)
      - [`/generate-report` – Generate PDF Report](#generate-report--generate-pdf-report)
  - [Frontend Interface (Vue 3 + Vuetify)](#frontend-interface-vue-3--vuetify)
    - [Technologies Used](#technologies-used)
    - [Features](#features)

## Overview

This project enables users to generate comprehensive PDF reports of all their **YAM v1** transactions on the Gnosis blockchain.

This project consists of **3 core modules**:

1. **Indexing Module** (Python) – Tracks and stores all YAM blockchain transactions in a local database.  
2. **API & PDF Generation Module** (Python) – Provides an API endpoint to generate and download PDF reports.  
3. **Frontend Interface** (Vue.js + Vuetify) – A minimal UI that allows the user to enter their parameters and download the PDF.

---

## System Requirements

- Python 3.9+
- Node.js 18+

---

## Installation Guide

### Step 1 – Configure *config.json*

Upload to the root project directory the `config.json` file. See the `config_example.json` as a template to complete:

```json
{
    "w3_urls": [
        "https://gnosis-mainnet.blastapi.io/...",
        "https://lb.nodies.app/v1/...",
        "https://gnosis-mainnet.core.chainstack.com/..."
      ],
    "db_path": "YAM_events.db",
    "api_port" : 5000,
    "realtokens_api_url" : "https://api.realtoken.community/v1/token",
    "the_graph_api_key" : "...",
    "subgraph_url" : "https://gateway.thegraph.com/api/subgraphs/id/7xsjkvdDtLJuVkwCigMaBqGqunBvhYjUSPFhpnGL1rvu"
}
```

2. **Install Python Dependencies**

```bash
# Optional but recommended: create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install packages listed in requirements.txt
pip install -r requirements.txt
```

3. **Install Frontend Dependencies**

```bash
# Change directory to the 'UI' folder (where the frontend code is
cd UI

# Install all dependencies listed in package.json and build the UI
npm install
npm run build
```

4. **Initialize the indexing module**  
(database creation and historical data backfill - this step might take a while)
```bash
python3 -m yam_indexing_module.initialize_indexing_module
```

---

## Running the Project

>Since multiple components need to run simultaneously, consider using screen or tmux to keep each process running in its own terminal session. This is especially helpful on remote servers or when you want processes to keep running after you disconnect.

#### Start the Indexing Service
```bash
python3 -m yam_indexing_module.main_indexing
```

#### Start the API Server
```bash
python3 pdf_generator_module/start_api.py
```
You can verify that the API server is running by visiting the following health check endpoint in your browser:
```http://[your-domain]:[public-api-port]/api/health```
> **Note**:
> - The **internal port** on which the API actually listens is defined in the `config.json` file under the key `api_port`. This is the port your API process binds to inside the container or on the server.
>
> - The **public API port**, i.e., the one exposed to the outside world and used by the frontend (UI), is defined in the environment file:
>   - In development, it's set in `.env.development` as `VITE_API_PORT`
>   - In production, it's set in `.env.production` as `VITE_API_PORT`
>
> - In development, the `VITE_API_PORT` value typically **matches** the `api_port` in `config.json`, since no reverse proxy is used (e.g., both set to `5000`).
>
> - In production, they may **differ**: the API might listen internally on a port like `5000` (from `config.json`), while a reverse proxy like Nginx forwards public traffic from port `443` (or another) to this internal port.  
>   The frontend uses `VITE_API_PORT` to know which port to call.

#### Start the Web Interface
The frontend is built as static files located in the ```UI/dist``` directory after running ```npm run build```.
Deploy these static files using your existing web server infrastructure (Nginx, Apache, IIS, etc.) or cloud hosting service. The specific deployment method depends on your infrastructure setup and is outside the scope of this guide.

>Note: The built application in UI/dist contains standard static HTML, CSS, and JavaScript files that can be served by any web server.

---

## Technical analysis and module details

### Indexing Module (Python)

This module is responsible for tracking all YAM v1 transactions on the Gnosis blockchain and storing them in a local SQLite database.

#### How It Works

#### Initialization script

1. **Database Initialization**  
   A one-time script initializes the local database by creating three core tables:

   - `offers`: stores all offers ever created on the YAM contract along with their status (In progress, sold out, deleted).
   - `offer_events`: stores all events related to each offer (creation, modification, purchase, deletion).
   - `indexing_status`: tracks the indexing progress by recording the last indexed block.

2. **Historical Backfill with The Graph**  
   Within this initialization script, the module queries a YAM-specific subgraph hosted on The Graph. This allows for a full backfill of past transactions from the contract’s deployment up to the latest block, ensuring historical completeness.

#### Main script to run the indexing service

1. **Startup Synchronization**  
   When the indexing service starts, it checks for any gap between the last indexed block and the current head of the blockchain. If needed, it fills the gap using The Graph to ensure continuity.

2. **Live Indexing Loop**  
   The core of the module runs in a continuous loop. It:

   - Fetches raw logs directly from the Gnosis blockchain using RPC endpoints.
   - Automatically switches between multiple RPCs if one fails.
   - Decodes the logs into structured event data.
   - Stores the results in the appropriate database tables.

3. **Periodic Backfill & Health Checks**  
   Every few cycles, the module performs a short backfill (e.g., the last few hours) via The Graph to ensure no transactions were missed. (This is also useful to confirm that the subgraph is still being actively used so that The Graph indexers won’t stop indexing)

#### Other considerations

**Data Format**  
   The database is designed to reflect raw on-chain data as closely as possible. For instance, numeric fields are stored in `uint256` format to avoid data loss or misinterpretation.

**Scalable and Resilient to Third-Party Failures**  
   The app’s indexing logic is built to scale: it performs a fixed number of RPC and subgraph queries, regardless of how many users or transactions there are. This means the system won’t generate more load—or require a paid plan—as usage grows. All user queries rely on a local database that stays up to date via a background sync, not per-user reads from The Graph or the chain.  
   In addition, this setup has the advantage of being resilient to downtimes of third-party indexers like The Graph. Since the app queries its own database instead of relying on external services at runtime, it continues to function normally even if those indexers become unavailable.

### API & PDF Generation Module (Python)

This module provides a RESTful API (using flask python library) to generate PDF reports. The PDF is generated using the `reportlab` library and includes detailed transaction data over a given date range.


#### Endpoints:
  - `/health` – Simple health check endpoint to verify the API is alive
  - `/generate-report` – Main endpoint to generate and download a PDF report
 


##### `/health` – Health Check
- **Method:** `GET`
- **Returns:** JSON object with current status and timestamp.

##### `/generate-report` – Generate PDF Report

- **Method:** `POST`
- **Content-Type:** `application/json`
- **Returns:** A generated PDF file (`application/pdf`) containing transaction summaries based on the input filters.

##### Request JSON Body

```json
{
  "start_date": "2024-09-01T00:00:00Z",
  "end_date": "2024-09-30T23:59:59Z",
  "event_type": ["buy", "sell", "exchange"],
  "user_addresses": ["0x123...", "0xabc..."],
  "display_tx_column": true
}
```

- **`start_date`** and **`end_date`** must be valid [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) UTC strings (e.g., `"2024-09-01T00:00:00Z"`).

- **`event_type`** must be a list containing one or more of the following values: `"buy"`, `"sell"`, and/or `"exchange"`.

- **`user_addresses`** must be a list of valid Ethereum addresses. Checksum casing is not required; addresses will be converted automatically.

- **`display_tx_column`** (`boolean`): whether to display the transaction hash column in the final PDF.

> Note: the module can be run in dev mode using the following command:  
```python3 -m pdf_generator_module.api.dev_run_api```

### Frontend Interface (Vue 3 + Vuetify)

This is the front-end module for the YAM transaction PDF generator. It provides a modern, mobile-friendly interface allowing users to select wallet addresses, date ranges, transaction types, and other display options. The UI then submits these parameters to the backend API and downloads a customized PDF report.



#### Technologies Used

- **Vue 3** with Composition API
- **Vuetify 3** for material design components
- **Custom styling** for a gradient hero section and elegant glassmorphic UI

#### Features

- Add one or more **Ethereum wallet addresses**
- Pick a **start and end date** (with validation)
- Choose one or more **transaction types**: `Buy`, `Sell`, `Exchange`
- Optional **transaction URL column** (Gnosisscan link)
- Instant validation for wallet addresses and dates
- Clear UI feedback messages (e.g., errors, success, loading states)