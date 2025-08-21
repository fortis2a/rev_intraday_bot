# Trading System Database Task Scheduler
# Set up Windows Task Scheduler for automated data collection and reporting

# Task 1: Daily Data Collection at 4:15 PM
schtasks /create /tn "Trading_DataCollection" /tr "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System\run_daily_collection.bat" /sc daily /st 16:15 /f

# Task 2: Enhanced Report Generation at 4:30 PM  
schtasks /create /tn "Trading_ReportGeneration" /tr "C:\Users\will7\OneDrive - Sygma Data Analytics\Stock Trading\Scalping Bot System\run_enhanced_report.bat" /sc daily /st 16:30 /f

Write-Host "✅ Scheduled tasks created successfully:"
Write-Host "📊 Data Collection: Daily at 4:15 PM"
Write-Host "📋 Report Generation: Daily at 4:30 PM"
Write-Host ""
Write-Host "To view scheduled tasks:"
Write-Host "schtasks /query /tn Trading_DataCollection"
Write-Host "schtasks /query /tn Trading_ReportGeneration"
Write-Host ""
Write-Host "To delete tasks if needed:"
Write-Host "schtasks /delete /tn Trading_DataCollection /f"
Write-Host "schtasks /delete /tn Trading_ReportGeneration /f"
