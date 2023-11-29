from dotenv import load_dotenv
import argparse
import os

load_dotenv()

#### ARGUMENTS ###############################################################################################
# Initialize argparse, define command-line arguments, create and populate arg groups #
ap = argparse.ArgumentParser(description="Leakdown Tester Script")

# General test configuration arguments
configGroup = ap.add_argument_group()
configGroup.add_argument("--target", choices=["local", "heroku", "cloud"], default="local", help="Target PFP environment: use 'local', 'heroku', or 'cloud'.")
configGroup.add_argument("--tests", type=int, default=1, help="Number of Leakdown Tests to perform.")
configGroup.add_argument("--threads", type=int, default=1, help="Number of threads to run Leakdown Tests on in parallel.")
configGroup.add_argument("--respond", action="store_true", help="SetTrue: Log subset of API response keys.")
configGroup.add_argument("--saveResponse", action="store_true", help="SetTrue: Save entire API response(s) to text file(s).")
configGroup.add_argument("--debug", action="store_true", help="SetTrue: Shows debug-focused console logger.")
configGroup.add_argument("--saveLog", action="store_true", help="SetTrue: Writes LDT logs to text file.")
configGroup.add_argument("--report", action="store_true", help="SetTrue: Shows report of latest run, with selected message measures, templates, and causal pathway summaries.")
#
# Behavior-setting arguments
behaviorGroup = ap.add_mutually_exclusive_group() # Mutually exclude args that set behavior
behaviorGroup.add_argument("--useCSV", action="store_true", help="SetTrue: Use performance data JSON payload from CSV file.")
behaviorGroup.add_argument("--postwoman", action="store_true", help="SetTrue: Use performance data JSON payload from addendum file.")
behaviorGroup.add_argument("--useGit", type=str, default=None, help="Address of GitHub input message file to send pipeline.")
behaviorGroup.add_argument("--persona", choices=["alice", "bob", "chikondi", "deepa", "eugene", "fahad", "gaile"], help="Select a persona for testing.")
behaviorGroup.add_argument("--allPersonas", action="store_true", help="SetTrue: Test all knowledgebase persona input message files.")
behaviorGroup.add_argument("--CP", choices=["goal_approach","goal_gain","goal_loss","improving","social_approach","social_better","social_gain","social_loss","social_worse","worsening","all"], help="Select a causal pathway (acronym) for testing.")
behaviorGroup.add_argument("--allCPs", action="store_true", help="SetTrue: Test all causal-pathway-specific input message files.")
behaviorGroup.add_argument("--sendLocals", type=int, default=1, help="Number of locally-hosted input messages to send.")
#
#  Output V&V arguments
verificationGroup = ap.add_mutually_exclusive_group() # Mutually exclude V&V operations
verificationGroup.add_argument("--vignVerify", action="store_true", help="SetTrue: Compare output message keys against vignette data library.")
verificationGroup.add_argument("--pilotVerify", action="store_true", help="SetTrue: Compare output message keys against pilot's restricted vignette data library.")
verificationGroup.add_argument("--cpVerify", action="store_true", help="SetTrue: Compare input and output causal pathway for match.")
#
# CSV payload config arguments
ap.add_argument("--RI", type=int, default=0, help="First row of data to read from CSV.")
ap.add_argument("--RF", type=int, default=12, help="Last row of data to read from CSV.")
ap.add_argument("--CI", type=int, default=0, help="First column to read from CSV.")
ap.add_argument("--CF", type=int, default=10, help="Final column to read from CSV.")
# 
# Required file pathing (argument specified)
ap.add_argument("--csv", type=str, default=None, help="CSV filepath; when specified overwrites 'CSVPATH', uses CSV data for JSON payload(s).")
ap.add_argument("--servAcc", type=str, default=None, help="Filepath to the service account file to read from" )
#
args = ap.parse_args()      # Parse initialization arguments


##### Assign Environmental Variables, with overwrite logic where appropriate #########
args.pfp         = os.environ.get("PFP")
args.audience    = os.environ.get("TARGET_AUDIENCE")
args.checkCP     = args.cpVerify if args.CP != None or args.allCPs    else None             # Only allow CP check if testing CPs
args.perfCSVPath = args.csv      if args.csv != None     else    os.environ.get("CSVPATH")  # Path to performance CSV data
args.SAPath      = args.servAcc  if args.servAcc != None else    os.environ.get("SAPATH")   # Path to service account file