# Qualifyze Verification System - Usage Guide

## Overview

The Qualifyze Verification and Analytics System is a Go-based application that validates audit requests following a comprehensive validation flow including Customer, Supplier, and Internal QA checks.

## Building the Application

```bash
# Download dependencies
go mod tidy

# Build the application
go build -o qualifyze .
```

## Running the Application

```bash
# Run with default data directory (./data)
./qualifyze

# Run with custom data directory
./qualifyze /path/to/data
```

The server will start on port 8080 by default. You can change the port by setting the `PORT` environment variable:

```bash
PORT=9000 ./qualifyze
```

## API Endpoints

### Health Check
```bash
GET /api/health
```

Example:
```bash
curl http://localhost:8080/api/health
```

### Reload CSV Data
```bash
POST /api/load
```

Example:
```bash
curl -X POST http://localhost:8080/api/load
```

### Validate All Requests
```bash
POST /api/validate
```

Example:
```bash
curl -X POST http://localhost:8080/api/validate | jq .
```

Response:
```json
{
  "status": "success",
  "total_requests": 500,
  "valid_requests": 212,
  "invalid_requests": 288,
  "results": {
    "REQ00001": {
      "Valid": false,
      "Warnings": [],
      "Errors": ["Supplier 122 has incomplete information"]
    },
    ...
  }
}
```

### Validate Specific Request
```bash
POST /api/validate/request?id=REQ00001
```

Example:
```bash
curl -X POST "http://localhost:8080/api/validate/request?id=REQ00001" | jq .
```

Response:
```json
{
  "status": "success",
  "request_id": "REQ00001",
  "result": {
    "Valid": false,
    "Warnings": [],
    "Errors": ["Supplier 122 has incomplete information"]
  }
}
```

## Validation Flow

The system implements the following three-step validation process:

### 1. Customer Validation
- Checks if customer information is complete (ID, contact info)
- Verifies customer has available credits
- If validation fails, request is rejected with appropriate error message

### 2. Supplier Validation
- Checks if supplier information is complete
- Verifies supplier is not blacklisted
- Checks supplier availability (warning only)
- If validation fails, request is rejected

### 3. Internal QA Validation
- Checks if quality officer is assigned
- Verifies quality officer exists in database
- Validates required request fields (requested standard)
- If validation fails, request is rejected

## CSV File Structure

The application expects the following CSV files in the data directory:

- `data_requests.csv` - Audit requests
- `credits.csv` - Customer credit information
- `suppliers.csv` - Supplier information
- `quality_officers.csv` - Internal QA officers
- `supplier_blacklist.csv` - Blacklisted suppliers

## Logging

All processing is logged to the console with timestamps and file/line information. The logging includes:

- Data loading progress
- Validation steps for each request
- Warnings and errors encountered
- API request handling

## Example Run

```bash
$ ./qualifyze
2025/11/11 13:42:43 =================================================
2025/11/11 13:42:43 Qualifyze Verification and Analytics System
2025/11/11 13:42:43 =================================================
2025/11/11 13:42:43 Starting to load CSV data from directory: ./data
2025/11/11 13:42:43 Loading data_requests.csv...
2025/11/11 13:42:43 Loaded 500 requests
2025/11/11 13:42:43 Loading credits.csv...
2025/11/11 13:42:43 Loaded 2712 credits
2025/11/11 13:42:43 Loading suppliers.csv...
2025/11/11 13:42:43 Loaded 150 suppliers
2025/11/11 13:42:43 Loading quality_officers.csv...
2025/11/11 13:42:43 Loaded 15 quality officers
2025/11/11 13:42:43 Loading supplier_blacklist.csv...
2025/11/11 13:42:43 Loaded 12 blacklisted suppliers
2025/11/11 13:42:43 Successfully loaded all CSV data
2025/11/11 13:42:43 Starting server on port 8080...
2025/11/11 13:42:43 =================================================
2025/11/11 13:42:43 Available endpoints:
2025/11/11 13:42:43   GET  /api/health            - Health check
2025/11/11 13:42:43   POST /api/load              - Reload CSV data
2025/11/11 13:42:43   POST /api/validate          - Validate all requests
2025/11/11 13:42:43   POST /api/validate/request  - Validate specific request
2025/11/11 13:42:43 =================================================
```

## Testing

Run a quick test of the system:

```bash
# Start the server in one terminal
./qualifyze

# In another terminal, run these commands:

# Check health
curl http://localhost:8080/api/health

# Validate all requests
curl -X POST http://localhost:8080/api/validate | jq '{status, total_requests, valid_requests, invalid_requests}'

# Validate specific request
curl -X POST "http://localhost:8080/api/validate/request?id=REQ00001" | jq .
```
