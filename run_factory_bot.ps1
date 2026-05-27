Set-Location "C:\Users\honra\HONRAI_FACTORY"

$python = "C:\Users\honra\HONRAI_FACTORY\.venv\Scripts\python.exe"
$script = "C:\Users\honra\HONRAI_FACTORY\bot\factory_bot.py"
$stdout = "C:\Users\honra\HONRAI_FACTORY\logs\bot_stdout.log"
$stderr = "C:\Users\honra\HONRAI_FACTORY\logs\bot_stderr.log"
$botlog = "C:\Users\honra\HONRAI_FACTORY\logs\bot.log"

while ($true) {
    Add-Content -Path $botlog -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [INFO] launcher: starting bot"
    & $python $script >> $stdout 2>> $stderr
    Add-Content -Path $botlog -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [ERROR] launcher: bot stopped, restarting in 5 seconds"
    Start-Sleep -Seconds 5
}
