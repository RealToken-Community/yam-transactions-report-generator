# YAM Transactions Report Generator

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Prerequisites and Configuration](#prerequisites-and-configuration)
- [Installation & Execution](#installation--execution)
  - [Option A — Docker (Recommended)](#option-a--docker-recommended)
  - [Option B — Manual Installation (Without Docker)](#option-b--manual-installation-without-docker)
- [API Details: PDF Generation](#api-details-pdf-generation)
  - [Endpoints](#endpoints)
- [Frontend Interface (Vue 3 + Vuetify)](#frontend-interface-vue-3--vuetify)

## Overview

This project enables users to generate comprehensive PDF reports of all their **YAM v1** transactions on the Gnosis blockchain.

This project consists of **2 modules**:

1. **PDF Generation API** (Python) – Provides an API endpoint to generate and download PDF reports.  
2. **Frontend Interface** (Vue.js + Vuetify) – A minimal UI that allows the user to enter their parameters and download the PDF.

---

## System Requirements

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional but recommended)

---

## Prerequisites and configuration

### Prerequisites

This project cannot function on its own. It depends on an external postgres database generated and maintained by the **YAM Indexing** project. The YAM Indexing application must be installed and running on its own.

For more information, see the [yam-indexing](https://github.com/RealToken-Community/yam-indexing) project.


### Configure Environment Variables

An example configuration file is provided: `.env.example`.  
Copy it to `.env` and update the values with your own secrets.

```env
REALTOKENS_API_URL=https://api.realtoken.community/v1/token

API_PORT_INTERNAL=5000

# Allow any app from realtoken.community (*.realtoken.community)
CORS_ORIGIN_REGEX=^https?://([a-z0-9-]+\.)*realtoken\.community$
# or allow any origin
#CORS_ORIGIN_REGEX=.*

# Postgres DB
POSTGRES_DB=yam_events
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_READER_USER_NAME=yam-indexing-reader
POSTGRES_READER_USER_PASSWORD=

# Telegram alerts [optional]
TELEGRAM_ALERT_BOT_TOKEN=
TELEGRAM_ALERT_GROUP_ID=
```

> **Note:**    
> For alerts, you can configure a Telegram bot and a Telegram group: the bot (using `TELEGRAM_ALERT_BOT_TOKEN`) must be added to the telegram chat group (`TELEGRAM_ALERT_GROUP_ID`) to receive automatic notifications about critical events such as failures or application stops.

## Installation & Execution

### Option A — Docker (Recommended)

The project includes a **ready-to-use Docker integration**.

From the **project root directory** (where `docker-compose.yml` is located), build
(or rebuild) and start the service with:

```bash
docker compose up --build -d
```

This single command:
- Rebuilds the image if the source code changed
- Recreates the existing container without duplication
- Starts the service from a clean state



To stop the service:

```bash
docker compose stop
```

> For detailed information about what is happening inside the Docker container, see the section below.

### Option B — Manual Installation (Without Docker)

#### 1. Create and Activate a Python Virtual Environment

```bash
# Optional but recommended: create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Install python (API) Dependencies

```bash
pip install -r requirements.txt
```


#### 3. **Install Frontend Dependencies**

```bash
# Change directory to the 'UI' folder (where the frontend code is)
cd UI

# Install all dependencies listed in package.json and build the UI
npm install
npm run build
```


#### 4. Running the Project

>When not using the recommended Docker setup, the different application instances must be managed independently. This includes running the Python-based API as a dedicated process, as well as building the frontend assets and serving them through a web server of choice. Each instance must be started, configured, and maintained separately.

##### Running the API Server

The API can be started in different ways depending on the operating system and execution context. Below are the supported commands.

```bash
# Linux (Production-like setup)
gunicorn -w 1 --threads 1 -b 0.0.0.0:5000 API.core.app:create_app()

# Windows (Production)
waitress-serve --listen=0.0.0.0:5000 --threads=1 --call "API.core.app:create_app"

# Windows (dev mode)
python -m API.core.dev_run_api
```

Once the API is running, its availability can be checked using the health endpoint:
```text
http://<your-domain>:<public-api-port>/api/health
```

>**Note on port Configuration and Environment Variables**
>The API and the frontend rely on different environment variables to determine which ports are used internally and which are exposed publicly.
>
>- **API internal port**  
>  The port on which the API process listens is defined in the `.env` file using the `API_PORT_INTERANL` variable.
>
>- **Public API port (used by the frontend)**  
>  The port used by the frontend (UI) to reach the API is defined by `VITE_API_PORT`:
>  - In production, this is set in `.env.production`
>  - In development, this is set in `.env.development`
>
>  For standard configurations, this value can be set to `80` or `443`, allowing API calls without explicitly specifying a port in the URL.
>
>- **Development vs Production behavior**  
>  In development, `VITE_API_PORT` usually matches `API_PORT_INTERANL` since no reverse proxy is involved (for example, both set to `5000`).  
>  In production, these values often differ: the API may listen internally on a port such as `5000`, while a reverse proxy (e.g. Nginx) exposes the API publicly on port `443` and forwards traffic to the internal port.

##### Running the Web Interface
The frontend is built as static files located in the ```UI/dist``` directory after running ```npm run build```.
Deploy these static files using your existing web server infrastructure (Nginx, Apache, IIS, etc.) or cloud hosting service. The specific deployment method depends on your infrastructure setup and is outside the scope of this guide.

>Note: The built application in UI/dist contains standard static HTML, CSS, and JavaScript files that can be served by any web server.

---


## API details: PDF generation

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
```python3 -m api.core.dev_run_api```

## Frontend Interface (Vue 3 + Vuetify)

This is the front-end module for the YAM transaction PDF generator. It provides a modern, mobile-friendly interface allowing users to select wallet addresses, date ranges, transaction types, and other display options. The UI then submits these parameters to the backend API and downloads a customized PDF report.

### Technologies Used

- **Vue 3** with Composition API
- **Vuetify 3** for material design components
- **Custom styling** for a gradient hero section and elegant glassmorphic UI

### Features

- Add one or more **Ethereum wallet addresses**
- Pick a **start and end date** (with validation)
- Choose one or more **transaction types**: `Buy`, `Sell`, `Exchange`
- Optional **transaction URL column** (Gnosisscan link)
- Instant validation for wallet addresses and dates
- Clear UI feedback messages (e.g., errors, success, loading states)
