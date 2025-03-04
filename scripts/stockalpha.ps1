# scripts/stockalpha.ps1

# Set environment variables
$env:PYTHONPATH = (Get-Location).Path

# Execute the Python script with arguments
python src/stockalpha/main.py $args
