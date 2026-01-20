"""
Sample data generator for Bank Alerts Workflow
This script generates sample suspicious bank movement alerts for testing
"""

from azure.cosmos import CosmosClient, PartitionKey
import random
from datetime import datetime, timedelta
import os

# Sample data templates
ALERT_TYPES = [
    "Large Withdrawal",
    "Foreign Transaction",
    "Multiple Small Transactions",
    "Unusual Purchase Pattern",
    "High-Risk Merchant",
    "Geographic Anomaly"
]

DESCRIPTIONS = [
    "Unusual large withdrawal detected from ATM in foreign country",
    "Multiple transactions from high-risk geographic location",
    "Pattern of small transactions consistent with money laundering",
    "Purchase from merchant flagged for fraudulent activity",
    "Transaction amount significantly exceeds normal spending pattern",
    "Card used in location inconsistent with recent usage pattern"
]


def generate_sample_alerts(count: int = 20) -> list:
    """Generate sample bank alerts"""
    alerts = []
    base_time = datetime.utcnow()
    
    for i in range(count):
        alert_id = f"alert-{i+1:03d}"
        account_number = f"{random.randint(1000000000, 9999999999)}"
        transaction_id = f"txn-{random.randint(100000, 999999)}"
        amount = round(random.uniform(500, 50000), 2)
        risk_score = round(random.uniform(0.6, 1.0), 2)
        
        alert = {
            "id": alert_id,
            "account_number": account_number,
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": "USD",
            "timestamp": (base_time - timedelta(minutes=random.randint(0, 1440))).isoformat() + "Z",
            "alert_type": random.choice(ALERT_TYPES),
            "description": random.choice(DESCRIPTIONS),
            "risk_score": risk_score,
            "recipient_phone": f"+1{random.randint(2000000000, 9999999999)}",
            "status": "pending"
        }
        
        alerts.append(alert)
    
    return alerts


def insert_sample_data():
    """Insert sample data into Cosmos DB"""
    
    # Get configuration from environment
    cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT")
    cosmos_key = os.environ.get("COSMOS_KEY")
    database_name = os.environ.get("COSMOS_DATABASE", "BankingDB")
    container_name = os.environ.get("COSMOS_CONTAINER", "Alerts")
    
    if not cosmos_endpoint or not cosmos_key:
        print("❌ Please set COSMOS_ENDPOINT and COSMOS_KEY environment variables")
        return
    
    print(f"📊 Connecting to Cosmos DB: {cosmos_endpoint}")
    
    # Initialize Cosmos client
    client = CosmosClient(cosmos_endpoint, cosmos_key)
    
    # Get or create database
    database = client.create_database_if_not_exists(id=database_name)
    print(f"✅ Database: {database_name}")
    
    # Get or create container
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/account_number"),
        offer_throughput=400
    )
    print(f"✅ Container: {container_name}")
    
    # Generate and insert sample alerts
    print("\n📝 Generating sample alerts...")
    alerts = generate_sample_alerts(20)
    
    print(f"\n📤 Inserting {len(alerts)} sample alerts...")
    for alert in alerts:
        try:
            container.create_item(body=alert)
            risk_emoji = "🔴" if alert['risk_score'] >= 0.9 else "🟡" if alert['risk_score'] >= 0.7 else "🟢"
            print(f"  {risk_emoji} {alert['id']}: ${alert['amount']:,.2f} - Risk: {alert['risk_score']*100:.0f}%")
        except Exception as e:
            print(f"  ❌ Failed to insert {alert['id']}: {str(e)}")
    
    print("\n✅ Sample data insertion completed!")
    print(f"\nYou can now run the workflow to process these alerts:")
    print(f"  python workflow.py")


if __name__ == "__main__":
    insert_sample_data()
