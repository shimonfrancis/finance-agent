# run_monitor.py
import time
import schedule
from datetime import datetime
from graph.graph import app
from langchain_core.messages import HumanMessage

def run_analysis():
    """Run the full analysis pipeline"""
    print(f"\n{'='*50}")
    print(f"Running analysis at {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}\n")
    
    result = app.invoke(
        {"messages": [HumanMessage(content="Analyze stocks under 300 rupees with news")]},
        config={"configurable": {"thread_id": "monitor-session"}}
    )
    
    # Print recommendations
    if result.get("final_recommendations"):
        print("\n📊 RECOMMENDATIONS:")
        print(result["final_recommendations"])

def main():
    # Run immediately on start
    run_analysis()
    
    # Schedule to run every 15 minutes (adjust as needed)
    schedule.every(15).minutes.do(run_analysis)
    
    # Market hours: 9:15 AM - 3:30 PM IST
    print("Monitoring started. Press Ctrl+C to stop.")
    
    while True:
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute
        
        # Only run during market hours (9:15 AM - 3:30 PM)
        if (current_hour > 9 or (current_hour == 9 and current_minute >= 15)) and \
           (current_hour < 15 or (current_hour == 15 and current_minute <= 30)):
            schedule.run_pending()
        
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()