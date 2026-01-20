# Sample 3: Microsoft Agent Framework Workflow - Bank Alerts System

This sample demonstrates a Microsoft Agent Framework workflow that uses two agents to detect and notify customers about suspicious bank movements. The workflow reads alerts from Cosmos DB and sends notifications via WhatsApp through Azure Communication Services (ACS).

## Overview

This workflow coordinates two specialized agents:

1. **CosmosDB Alerts Reader Agent** - Reads suspicious bank movement alerts from Cosmos DB
2. **WhatsApp/ACS Sender Agent** - Sends alerts to customers via WhatsApp using Azure Communication Services

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Bank Alerts Workflow                          │
│                                                                  │
│  ┌───────────────────┐        ┌──────────────────────┐         │
│  │  CosmosDB Reader  │───────>│  WhatsApp ACS Sender │         │
│  │      Agent        │        │       Agent          │         │
│  └───────────────────┘        └──────────────────────┘         │
│          │                              │                       │
│          ▼                              ▼                       │
│   ┌─────────────┐              ┌──────────────┐               │
│   │  Cosmos DB  │              │   WhatsApp   │               │
│   │   (Alerts)  │              │ (via ACS)    │               │
│   └─────────────┘              └──────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- ✅ Read suspicious bank alerts from Cosmos DB with filtering
- ✅ Send formatted alerts via WhatsApp using Azure Communication Services
- ✅ Risk score-based filtering and prioritization
- ✅ Batch processing with configurable batch sizes
- ✅ Continuous monitoring mode
- ✅ Duplicate detection to prevent re-sending alerts
- ✅ Comprehensive error handling and logging
- ✅ Alert status tracking

## Prerequisites

- Python 3.8 or higher
- Azure Cosmos DB account with a database containing bank alerts
- Azure Communication Services (ACS) resource with WhatsApp channel configured
- WhatsApp Business Account connected to ACS

## Setup Instructions

### 1. Set Up Azure Cosmos DB

Create a Cosmos DB database and container:

```bash
# Create Cosmos DB account
az cosmosdb create \
  --name <cosmos-account-name> \
  --resource-group <resource-group> \
  --default-consistency-level Session

# Create database
az cosmosdb sql database create \
  --account-name <cosmos-account-name> \
  --resource-group <resource-group> \
  --name BankingDB

# Create container
az cosmosdb sql container create \
  --account-name <cosmos-account-name> \
  --database-name BankingDB \
  --name Alerts \
  --partition-key-path "/account_number" \
  --throughput 400
```

### 2. Set Up Azure Communication Services

```bash
# Create ACS resource
az communication create \
  --name <acs-resource-name> \
  --resource-group <resource-group> \
  --data-location UnitedStates

# Get connection string
az communication list-key \
  --name <acs-resource-name> \
  --resource-group <resource-group>
```

Configure WhatsApp channel in Azure Portal:
1. Go to your ACS resource
2. Navigate to "Channels" > "WhatsApp"
3. Follow the wizard to connect your WhatsApp Business Account
4. Note the Channel ID

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key
COSMOS_DATABASE=BankingDB
COSMOS_CONTAINER=Alerts

ACS_ENDPOINT=https://your-acs-resource.communication.azure.com
ACS_ACCESS_KEY=your-acs-access-key
WHATSAPP_CHANNEL_ID=your-whatsapp-channel-id

CONTINUOUS_MODE=false
INTERVAL_SECONDS=300
BATCH_SIZE=10
MIN_RISK_SCORE=0.7
```

### 5. Prepare Sample Data

Insert sample alerts into Cosmos DB:

```python
from azure.cosmos import CosmosClient

client = CosmosClient(url, credential=key)
database = client.get_database_client("BankingDB")
container = database.get_container_client("Alerts")

sample_alert = {
    "id": "alert-001",
    "account_number": "1234567890",
    "transaction_id": "txn-abc123",
    "amount": 5000.00,
    "currency": "USD",
    "timestamp": "2024-01-15T10:30:00Z",
    "alert_type": "Large Withdrawal",
    "description": "Unusual large withdrawal detected from ATM in foreign country",
    "risk_score": 0.85,
    "recipient_phone": "+1234567890",
    "status": "pending"
}

container.create_item(sample_alert)
```

### 6. Run the Workflow

**Single Batch Mode** (process once and exit):
```bash
python workflow.py
```

**Continuous Mode** (run continuously):
```bash
CONTINUOUS_MODE=true python workflow.py
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COSMOS_ENDPOINT` | Cosmos DB endpoint URL | Required |
| `COSMOS_KEY` | Cosmos DB access key | Required |
| `COSMOS_DATABASE` | Database name | `BankingDB` |
| `COSMOS_CONTAINER` | Container name | `Alerts` |
| `ACS_ENDPOINT` | ACS resource endpoint | Required |
| `ACS_ACCESS_KEY` | ACS access key | Required |
| `WHATSAPP_CHANNEL_ID` | WhatsApp channel ID | Required |
| `CONTINUOUS_MODE` | Run continuously | `false` |
| `INTERVAL_SECONDS` | Seconds between runs | `300` |
| `BATCH_SIZE` | Alerts per batch | `10` |
| `MIN_RISK_SCORE` | Minimum risk score | `0.7` |

## Alert Data Model

Each alert in Cosmos DB should have the following structure:

```json
{
  "id": "alert-001",
  "account_number": "1234567890",
  "transaction_id": "txn-abc123",
  "amount": 5000.00,
  "currency": "USD",
  "timestamp": "2024-01-15T10:30:00Z",
  "alert_type": "Large Withdrawal",
  "description": "Unusual activity detected",
  "risk_score": 0.85,
  "recipient_phone": "+1234567890",
  "status": "pending"
}
```

## WhatsApp Message Format

Alerts are sent with the following format:

```
🔴 **BANK ALERT - Suspicious Activity Detected**

**Alert ID:** alert-001
**Account:** 1234567890
**Transaction:** txn-abc123

**Amount:** USD 5,000.00
**Risk Score:** 85%
**Type:** Large Withdrawal

**Description:**
Unusual large withdrawal detected from ATM in foreign country

**Time:** 2024-01-15T10:30:00Z

Please review this transaction immediately and contact your bank 
if you did not authorize this activity.

For assistance, call: 1-800-BANK-HELP
```

## Workflow Process

1. **Read Alerts**: The CosmosDB Reader Agent queries for alerts with risk score above threshold
2. **Filter**: Alerts are filtered to avoid re-sending previously processed alerts
3. **Format**: Each alert is formatted into a user-friendly WhatsApp message
4. **Send**: The WhatsApp ACS Agent sends the message through Azure Communication Services
5. **Mark Sent**: Successfully sent alerts are marked in Cosmos DB
6. **Repeat**: In continuous mode, the workflow repeats after the specified interval

## Deployment

### Deploy as Azure Container Instance

```bash
# Build container
docker build -t bank-alerts-workflow .

# Push to ACR
az acr build --registry <acr-name> --image bank-alerts-workflow:latest .

# Deploy to ACI
az container create \
  --resource-group <rg-name> \
  --name bank-alerts-workflow \
  --image <acr-name>.azurecr.io/bank-alerts-workflow:latest \
  --environment-variables \
    COSMOS_ENDPOINT=$COSMOS_ENDPOINT \
    COSMOS_KEY=$COSMOS_KEY \
    ACS_ENDPOINT=$ACS_ENDPOINT \
    ACS_ACCESS_KEY=$ACS_ACCESS_KEY \
    WHATSAPP_CHANNEL_ID=$WHATSAPP_CHANNEL_ID \
    CONTINUOUS_MODE=true
```

### Deploy as Azure Function

The workflow can also be deployed as an Azure Function with a timer trigger:

```python
import azure.functions as func
from workflow import workflow

async def main(mytimer: func.TimerRequest) -> None:
    result = await workflow.process_alerts()
    logging.info(f"Processed alerts: {result}")
```

## Monitoring and Logging

The workflow provides comprehensive logging:

- Alert reading from Cosmos DB
- Message sending status
- Error details and stack traces
- Processing statistics

Example log output:
```
2024-01-15 10:30:00 - INFO - Starting alerts processing workflow (batch_size=10)
2024-01-15 10:30:01 - INFO - Reading alerts from Cosmos DB (limit=10, min_risk=0.7)
2024-01-15 10:30:02 - INFO - Successfully retrieved 5 alerts
2024-01-15 10:30:03 - INFO - Sending alert alert-001 via WhatsApp to +1234567890
2024-01-15 10:30:04 - INFO - Alert alert-001 sent successfully
2024-01-15 10:30:09 - INFO - Workflow completed: 5 sent, 0 failed out of 5 alerts
```

## Error Handling

The workflow includes comprehensive error handling:

- **Cosmos DB Connection Errors**: Logged and workflow continues
- **WhatsApp Send Failures**: Logged, alert remains pending for retry
- **Rate Limiting**: Built-in delays to avoid rate limits
- **Network Timeouts**: Configurable timeouts with fallback

## Security Best Practices

1. **Store Keys Securely**: Use Azure Key Vault for storing credentials
2. **Rotate Keys**: Regularly rotate Cosmos DB and ACS keys
3. **Network Security**: Use private endpoints for Cosmos DB
4. **Access Control**: Use RBAC for resource access
5. **Encrypt Data**: Enable encryption at rest and in transit

## Troubleshooting

### No alerts are being processed
- Verify alerts exist in Cosmos DB with risk_score >= MIN_RISK_SCORE
- Check Cosmos DB connection and credentials
- Verify the query syntax and parameters

### WhatsApp messages not sending
- Verify ACS WhatsApp channel is properly configured
- Check that phone numbers are in E.164 format (+country_code_phone_number)
- Ensure WhatsApp Business Account is active
- Check ACS quota and limits

### High risk scores not prioritized
- Adjust MIN_RISK_SCORE environment variable
- Verify risk_score field in alerts
- Check query ORDER BY clause

## Next Steps

- Add SMS fallback for WhatsApp delivery failures
- Implement alert acknowledgment workflow
- Add metrics and dashboards
- Support for multiple notification channels
- Implement alert escalation rules
- Add customer response handling

## Resources

- [Azure Cosmos DB Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/)
- [Azure Communication Services Documentation](https://docs.microsoft.com/en-us/azure/communication-services/)
- [WhatsApp Business Platform](https://developers.facebook.com/docs/whatsapp)
- [Microsoft Agent Framework](https://github.com/microsoft/agents)

## License

MIT License - See LICENSE file for details
