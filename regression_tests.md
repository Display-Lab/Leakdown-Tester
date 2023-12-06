# Regression test commands for Leakdown Tester Verification:
### Remote access to GitHub, sending to cloud instance
- Tests usegit, remote fetching, personas, cloud authentication, response handling, response reports, throttling, low volume, persona autoverification, log level modification
```zsh
python3 ldt.py --target cloud --allPersonas --pilotVerify --report  --loglvl trace
```
### Causal pathway testing with verification
```zsh
python3 ldt.py --target heroku --allCPs --cpVerify
```
### Heroku server, local files, log saving, response saving, local file autoverification
- Tests local JSON file sending, log and response local file generation, multiple tests, multithreads, response report with multithreading
```zsh
python3 ldt.py --target heroku --sendLocals 1 --saveLog --saveResponse --tests 2 --threads 2 --report
```

### CSV function testing
- CSV file sending, multithreading
```zsh
python3 ldt.py --target heroku --useCSV --RF 12
```