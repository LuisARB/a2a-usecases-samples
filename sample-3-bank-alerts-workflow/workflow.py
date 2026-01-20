"""
Microsoft Agent Framework Workflow - Bank Alerts System
This workflow uses two agents:
1. CosmosDB Alerts Reader Agent - Reads suspicious bank movement alerts
2. WhatsApp/ACS Sender Agent - Sends alerts via WhatsApp through Azure Communication Services
"""

import os
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BankAlert:
    """Represents a suspicious bank movement alert"""
    alert_id: str
    account_number: str
    transaction_id: str
    amount: float
    currency: str
    timestamp: str
    alert_type: str
    description: str
    risk_score: float
    recipient_phone: str


class CosmosDBReader:
    """Agent that reads suspicious bank movement alerts from Cosmos DB"""
    
    def __init__(
        self,
        cosmos_endpoint: str,
        cosmos_key: str,
        database_name: str,
        container_name: str
    ):
        self.cosmos_endpoint = cosmos_endpoint
        self.cosmos_key = cosmos_key
        self.database_name = database_name
        self.container_name = container_name
        
    async def read_alerts(
        self, 
        limit: int = 10,
        min_risk_score: float = 0.7
    ) -> List[BankAlert]:
        """
        Read suspicious bank movement alerts from Cosmos DB
        
        Args:
            limit: Maximum number of alerts to retrieve
            min_risk_score: Minimum risk score to filter alerts
            
        Returns:
            List of BankAlert objects
        """
        logger.info(f"Reading alerts from Cosmos DB (limit={limit}, min_risk={min_risk_score})")
        
        # Note: In production, use azure-cosmos SDK
        # This is a simplified version using REST API
        
        headers = {
            "Authorization": self.cosmos_key,
            "Content-Type": "application/json",
            "x-ms-version": "2018-12-31",
            "x-ms-documentdb-isquery": "True"
        }
        
        query = {
            "query": f"SELECT * FROM c WHERE c.risk_score >= @minRisk ORDER BY c.timestamp DESC",
            "parameters": [
                {"name": "@minRisk", "value": min_risk_score}
            ]
        }
        
        url = (
            f"{self.cosmos_endpoint}/dbs/{self.database_name}/"
            f"colls/{self.container_name}/docs"
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=query,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        documents = data.get("Documents", [])[:limit]
                        
                        alerts = []
                        for doc in documents:
                            alert = BankAlert(
                                alert_id=doc.get("id", ""),
                                account_number=doc.get("account_number", ""),
                                transaction_id=doc.get("transaction_id", ""),
                                amount=doc.get("amount", 0.0),
                                currency=doc.get("currency", "USD"),
                                timestamp=doc.get("timestamp", ""),
                                alert_type=doc.get("alert_type", ""),
                                description=doc.get("description", ""),
                                risk_score=doc.get("risk_score", 0.0),
                                recipient_phone=doc.get("recipient_phone", "")
                            )
                            alerts.append(alert)
                        
                        logger.info(f"Successfully retrieved {len(alerts)} alerts")
                        return alerts
                    else:
                        logger.error(f"Cosmos DB error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Failed to read from Cosmos DB: {str(e)}")
            return []
    
    async def mark_alert_as_sent(self, alert_id: str) -> bool:
        """
        Mark an alert as sent in Cosmos DB
        
        Args:
            alert_id: The ID of the alert to update
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Marking alert {alert_id} as sent")
        
        # In production, implement actual Cosmos DB update
        # For now, return success
        return True


class WhatsAppACSAgent:
    """Agent that sends alerts via WhatsApp through Azure Communication Services"""
    
    def __init__(
        self,
        acs_endpoint: str,
        acs_access_key: str,
        whatsapp_channel_id: str
    ):
        self.acs_endpoint = acs_endpoint
        self.acs_access_key = acs_access_key
        self.whatsapp_channel_id = whatsapp_channel_id
        
    async def send_alert(self, alert: BankAlert) -> Dict[str, Any]:
        """
        Send an alert via WhatsApp using Azure Communication Services
        
        Args:
            alert: The BankAlert to send
            
        Returns:
            Dict containing send status and details
        """
        logger.info(f"Sending alert {alert.alert_id} via WhatsApp to {alert.recipient_phone}")
        
        # Format the alert message
        message = self._format_alert_message(alert)
        
        # Prepare ACS WhatsApp request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.acs_access_key}"
        }
        
        payload = {
            "channelRegistrationId": self.whatsapp_channel_id,
            "to": [alert.recipient_phone],
            "kind": "text",
            "content": message
        }
        
        url = f"{self.acs_endpoint}/messages:send?api-version=2023-11-01"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in [200, 201, 202]:
                        result = await response.json()
                        logger.info(f"Alert {alert.alert_id} sent successfully")
                        return {
                            "success": True,
                            "alert_id": alert.alert_id,
                            "message_id": result.get("id", ""),
                            "status": "sent"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"ACS error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "alert_id": alert.alert_id,
                            "error": f"ACS returned status {response.status}",
                            "details": error_text
                        }
        except Exception as e:
            logger.error(f"Failed to send alert via WhatsApp: {str(e)}")
            return {
                "success": False,
                "alert_id": alert.alert_id,
                "error": "Send failed",
                "details": str(e)
            }
    
    def _format_alert_message(self, alert: BankAlert) -> str:
        """
        Format a bank alert into a WhatsApp message
        
        Args:
            alert: The BankAlert to format
            
        Returns:
            Formatted message string
        """
        risk_emoji = "🔴" if alert.risk_score >= 0.9 else "🟡" if alert.risk_score >= 0.7 else "🟢"
        
        message = f"""
{risk_emoji} **BANK ALERT - Suspicious Activity Detected**

**Alert ID:** {alert.alert_id}
**Account:** {alert.account_number}
**Transaction:** {alert.transaction_id}

**Amount:** {alert.currency} {alert.amount:,.2f}
**Risk Score:** {alert.risk_score * 100:.0f}%
**Type:** {alert.alert_type}

**Description:**
{alert.description}

**Time:** {alert.timestamp}

Please review this transaction immediately and contact your bank if you did not authorize this activity.

For assistance, call: 1-800-BANK-HELP
""".strip()
        
        return message


class BankAlertsWorkflow:
    """
    Workflow that coordinates CosmosDB Reader and WhatsApp Sender agents
    """
    
    def __init__(
        self,
        cosmos_reader: CosmosDBReader,
        whatsapp_sender: WhatsAppACSAgent
    ):
        self.cosmos_reader = cosmos_reader
        self.whatsapp_sender = whatsapp_sender
        self.processed_alerts: List[str] = []
        
    async def process_alerts(
        self,
        batch_size: int = 10,
        min_risk_score: float = 0.7
    ) -> Dict[str, Any]:
        """
        Main workflow: Read alerts from Cosmos DB and send via WhatsApp
        
        Args:
            batch_size: Number of alerts to process in this batch
            min_risk_score: Minimum risk score threshold
            
        Returns:
            Dict containing processing results
        """
        logger.info(f"Starting alerts processing workflow (batch_size={batch_size})")
        
        # Step 1: Read alerts from Cosmos DB
        alerts = await self.cosmos_reader.read_alerts(
            limit=batch_size,
            min_risk_score=min_risk_score
        )
        
        if not alerts:
            logger.info("No alerts to process")
            return {
                "status": "completed",
                "alerts_processed": 0,
                "alerts_sent": 0,
                "alerts_failed": 0
            }
        
        # Step 2: Send each alert via WhatsApp
        results = []
        sent_count = 0
        failed_count = 0
        
        for alert in alerts:
            # Skip if already processed
            if alert.alert_id in self.processed_alerts:
                logger.info(f"Alert {alert.alert_id} already processed, skipping")
                continue
            
            # Send the alert
            send_result = await self.whatsapp_sender.send_alert(alert)
            results.append(send_result)
            
            if send_result.get("success"):
                sent_count += 1
                self.processed_alerts.append(alert.alert_id)
                
                # Mark as sent in Cosmos DB
                await self.cosmos_reader.mark_alert_as_sent(alert.alert_id)
            else:
                failed_count += 1
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        logger.info(
            f"Workflow completed: {sent_count} sent, {failed_count} failed "
            f"out of {len(alerts)} alerts"
        )
        
        return {
            "status": "completed",
            "alerts_processed": len(alerts),
            "alerts_sent": sent_count,
            "alerts_failed": failed_count,
            "results": results
        }
    
    async def run_continuous(
        self,
        interval_seconds: int = 300,
        batch_size: int = 10,
        min_risk_score: float = 0.7
    ):
        """
        Run the workflow continuously at specified intervals
        
        Args:
            interval_seconds: Time between workflow runs
            batch_size: Number of alerts per batch
            min_risk_score: Minimum risk score threshold
        """
        logger.info(f"Starting continuous workflow (interval={interval_seconds}s)")
        
        while True:
            try:
                result = await self.process_alerts(
                    batch_size=batch_size,
                    min_risk_score=min_risk_score
                )
                logger.info(f"Batch result: {result}")
                
            except Exception as e:
                logger.error(f"Error in continuous workflow: {str(e)}")
            
            # Wait for next interval
            await asyncio.sleep(interval_seconds)


# Configuration from environment variables
COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT", "https://your-cosmos-account.documents.azure.com:443/")
COSMOS_KEY = os.environ.get("COSMOS_KEY", "")
COSMOS_DATABASE = os.environ.get("COSMOS_DATABASE", "BankingDB")
COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER", "Alerts")

ACS_ENDPOINT = os.environ.get("ACS_ENDPOINT", "https://your-acs-resource.communication.azure.com")
ACS_ACCESS_KEY = os.environ.get("ACS_ACCESS_KEY", "")
WHATSAPP_CHANNEL_ID = os.environ.get("WHATSAPP_CHANNEL_ID", "")

# Initialize agents
cosmos_reader = CosmosDBReader(
    cosmos_endpoint=COSMOS_ENDPOINT,
    cosmos_key=COSMOS_KEY,
    database_name=COSMOS_DATABASE,
    container_name=COSMOS_CONTAINER
)

whatsapp_sender = WhatsAppACSAgent(
    acs_endpoint=ACS_ENDPOINT,
    acs_access_key=ACS_ACCESS_KEY,
    whatsapp_channel_id=WHATSAPP_CHANNEL_ID
)

# Initialize workflow
workflow = BankAlertsWorkflow(
    cosmos_reader=cosmos_reader,
    whatsapp_sender=whatsapp_sender
)


async def main():
    """Main entry point"""
    logger.info("🏦 Bank Alerts Workflow Starting")
    logger.info(f"📊 Cosmos DB: {COSMOS_ENDPOINT}")
    logger.info(f"📱 ACS Endpoint: {ACS_ENDPOINT}")
    
    # Check if running in continuous mode
    continuous_mode = os.environ.get("CONTINUOUS_MODE", "false").lower() == "true"
    
    if continuous_mode:
        interval = int(os.environ.get("INTERVAL_SECONDS", "300"))
        batch_size = int(os.environ.get("BATCH_SIZE", "10"))
        min_risk = float(os.environ.get("MIN_RISK_SCORE", "0.7"))
        
        logger.info(f"Running in continuous mode (interval={interval}s)")
        await workflow.run_continuous(
            interval_seconds=interval,
            batch_size=batch_size,
            min_risk_score=min_risk
        )
    else:
        # Run once
        batch_size = int(os.environ.get("BATCH_SIZE", "10"))
        min_risk = float(os.environ.get("MIN_RISK_SCORE", "0.7"))
        
        logger.info("Running in single-batch mode")
        result = await workflow.process_alerts(
            batch_size=batch_size,
            min_risk_score=min_risk
        )
        logger.info(f"Final result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
