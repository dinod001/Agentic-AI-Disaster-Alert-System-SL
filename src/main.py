import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.blocking import BlockingScheduler
from agents.monitor_agent import MonitorAgent
from notifiers.telegram_bot import send_alert
from utils.logger import setup_logger

logger = setup_logger("Main")

# Create the agent once — reuse every cycle
agent = MonitorAgent()


def run_cycle():
    """Run one full monitoring cycle: collect → analyse → generate alert → send."""
    logger.info("Starting monitoring cycle...")
    try:
        alert = agent.generate_report()
        if alert:
            logger.info("Alert generated successfully")
            sys.stdout.reconfigure(encoding="utf-8")
            timestamp = datetime.now().strftime("🕐 %Y-%m-%d %H:%M:%S")
            alert_with_time = f"{timestamp}\n\n{alert}"
            print("\n" + "=" * 60)
            print(alert_with_time)
            print("=" * 60 + "\n")
            send_alert(alert_with_time)
        else:
            logger.warning("No alert generated this cycle")
    except Exception as e:
        logger.error("Monitoring cycle failed: %s", e)


if __name__ == "__main__":
    logger.info("Disaster Alert System started - running every 1 hour")

    # Run immediately on start, then every hour
    run_cycle()

    scheduler = BlockingScheduler()
    scheduler.add_job(run_cycle, "interval", hours=1)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user")
