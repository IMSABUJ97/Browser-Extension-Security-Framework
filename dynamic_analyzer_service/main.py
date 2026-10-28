from fastapi import FastAPI, HTTPException
from core_analyzer.browser_manager import BrowserManager
import uvicorn
import asyncio
import uuid
import sys

app = FastAPI(title="Dynamic Analyzer API")

def calculate_risk_score(logs):
    if not logs:
        logs = {}
        
    score = 0
    network_logs = logs.get("network", [])
    if network_logs is None:
        network_logs = []
    score += len(network_logs) * 10
    
    dom_logs = logs.get("dom", [])
    if dom_logs is None:
        dom_logs = []
        
    for dom_log in dom_logs:
        if "password" in str(dom_log).lower() or "suspicious" in str(dom_log).lower():
            score += 50
            
    score = min(score, 100)
    
    if score >= 70:
        threat_level = "CRITICAL"
    elif score >= 40:
        threat_level = "HIGH"
    elif score >= 20:
        threat_level = "MEDIUM"
    else:
        threat_level = "LOW"
        
    return score, threat_level

@app.get("/")
async def root():
    return {"message": "Welcome to Dynamic Analyzer API"}


@app.post("/analyze/dynamic")
def trigger_analysis(extension_path: str, target_url: str):
    try:
        analysis_id = f"SIM-{str(uuid.uuid4())[:6].upper()}"
        
        
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        
        manager = BrowserManager(extension_path, target_url)
        
        
        raw_logs = new_loop.run_until_complete(manager.start_analysis(duration=10))
        new_loop.close()
        
        if raw_logs is None:
            raw_logs = {}
        
        risk_score, threat_level = calculate_risk_score(raw_logs)
        
        final_report = {
            "analysis_id": analysis_id,
            "extension_path": extension_path,
            "target_url": target_url,
            "risk_score": risk_score,
            "threat_level": threat_level,
            "behavioral_findings": {
                "network_activity": raw_logs.get("network", []),
                "dom_manipulations": raw_logs.get("dom", [])
            },
            "status": "Completed"
        }
        
        return final_report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed to run: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)