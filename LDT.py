from LDT_Addendum import vignAccPairs, payloadHeader, payloadFooter, ldtVersion, hitlistCP, hitlistIM, postwoman, pilotPairs
from google.oauth2 import service_account
import google.auth.transport.requests
from collections import defaultdict
from dotenv import load_dotenv
import threading
from threading import Barrier
from google.auth import crypt
from functools import reduce
from loguru import logger
import pandas as pd
import requests
import argparse
import certifi
import base64
import json
import time
import os
import sys
global pfp, audience, perfPath, servAccPath, chkCP

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


##### Assign Environmental Variables, ft. overwrite logic where appropriate #########
pfp         = os.environ.get("PFP")
audience    = os.environ.get("TARGET_AUDIENCE")
chkCP       = args.cpVerify if args.CP != None or args.allCPs    else None             # Only allow CP check if testing CPs
perfPath    = args.csv      if args.csv != None     else    os.environ.get("CSVPATH")  # Path to performance CSV data
servAccPath = args.servAcc  if args.servAcc != None else    os.environ.get("SAPATH")   # Path to service account file


#### Logging module configuration ######################################################
logger.remove()
log_level    = "DEBUG"         if args.debug       else "INFO"  # Set log level

# Create unified sink with standard and custom log levels
logger.level("RESPONSE", no=21, color="<cyan>")
logger.add(sys.stdout, level=log_level, format="<b><level>{level}</></> \t{message}")

# Save console log to file if asked
if args.saveLog:
    log_filename = 'Leakdown_Tests.log'  if args.saveLog   else None          
    logger.add(log_filename, level=log_level, format="<level>{level}</> \t| {message}")



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


##### Startup Functions ###############################################################
### Handle API endpoint, script behavior, and number of requests to send.
### V 0.4.3+ has integrated readback as configurations are set.

## Set script behavior for JSON content source (+ error handling and readback)...
def set_behavior():
    global perfPath
    logger.debug("RUNNING FUNCTION: 'set_behavior'...")
    # Error catcher for multiple JSON payload specification
    if perfPath != None and args.useGit != None:
        logger.warning("Multiple JSON payloads specified.\tContinuing with GitHub payload...\n")
    
    # Set behavior to use user-specified GitHub content (1st priority)
    elif args.useGit != None:      
        logger.info(f"Reading JSON data from GitHub file at {args.useGit}...")
        return "customGithub"
    
    # Set behavior to run single persona test (2nd)
    elif args.persona != None:
        logger.info("Reading one persona's JSON file from remote 'Personas' folder...")
        return "onePers"
    
    # Set behavior to run all persona tests (3rd)
    elif args.allPersonas:          
        logger.info("Reading all JSON files from remote 'Personas' folder...")
        return "allPers"

   # Set behavior to run single causal pathway test (4th)
    elif args.CP !=  None:          
        logger.info("Reading one JSON file from remote 'Causal Pathway Test Suite'...")
        return "oneCP"

   # Set behavior to run all causal pathway tests (5th)
    elif args.allCPs:          
        logger.info("Reading all JSON files from remote 'Causal Pathway Test Suite'...")
        return "allCPs"

    elif args.postwoman:
        logger.info("Using 'Postwoman' var in Addendum file as JSON payload...")
        return "postwoman"

    # Set behavior to use CSV content (last priority)
    elif args.useCSV:
        logger.info(f"Reading data from CSV file at '{perfPath}'...")
        logger.info(f"Reading in data with dimensions {args.RF - args.RI} by {args.CF - args.CI}...")
        return "CSV"
    
    # Set behavior to run local input_message files
    elif args.sendLocals != None:
        logger.info(f"Sending {args.sendLocals} local requests to API instance...")
        return "sendLocals"
    
    else:
        logger.critical("Could not set Behavior: No content specified for POST request.")
        exit(1)



## Configure API endpoint from argument...
def set_target():
    global pfp, oidcToken
    logger.debug("RUNNING FUNCTION: 'set_target'...")    
    
    # Local API target:
    if args.target == "local":
        pfp = "http://127.0.0.1:8000/createprecisionfeedback/"
    
    # Heroku API target:
    elif args.target == "heroku":
        pfp = "https://pfpapi.herokuapp.com/createprecisionfeedback/"
    
    # GCP API target (ft. token retrieval):
    elif args.target == "cloud":
        assert audience, "Target Audience not set. Exiting..."
        assert servAccPath, "Service Account Path not set. Exiting..."
        

        pfp = "https://pfp.test.app.med.umich.edu/createprecisionfeedback/"
        oidcToken = service_account.IDTokenCredentials.from_service_account_file(
        servAccPath,
        target_audience = audience,
        )
        logger.debug(f"Debug statements for GCP connection setup:\nTarget Audience:\n{audience}")
        logger.debug(f"Service Account Path:\n{servAccPath}")
        logger.debug(f"OIDCToken:{oidcToken}")
    
    else:
        logger.warning("Target not declared. Continuing with local PFP target.")
    
    # Readback endpoint target when successfull
    logger.info(f"Sending POST request(s) to API at '{pfp}'...\n")



## Calculate total number of POST requests script will try to send...
def calc_total_reqs(behavior):
    logger.debug("RUNNING FUNCTION: 'calc_total_reqs'...")
    if behavior == "allPers":
        totalRequests = len(hitlistIM) * args.tests * args.threads
    if behavior == "allCPs":
        totalRequests = len(hitlistCP) * args.tests * args.threads
    else:
        totalRequests = args.tests * args.threads
    
    logger.info(f"Sending {totalRequests} total POST requests...")
    return totalRequests





#### API Response Handling #########################################################
### These functions print out response output, handle making logs of response output,
### and validate responses against known-good data (vignette specifications)

## Print subset of JSON keys from API response...
def log_response_subset(response):
    logger.debug("RUNNING FUNCTION: 'log_response_subset'...")
    try:
        logger.opt(colors=True).log("RESPONSE", f"<b><cyan>API response contains keys:</></>")
        # Declare dict of keys in API response to log
        standard_keys = [
            'staff_number', 'message_instance_id', 'performance_month', 'selected_comparator',                  # 'Naked' keys
            'selected_candidate.display', 'selected_candidate.measure', 'selected_candidate.acceptable_by',     # Selected candidate keys
            'message.text_message'                                                                              # Message keys
        ]
        # Report image status vs returning full base64 key:
        logger.opt(colors=True).log("RESPONSE", f"<cyan>message.image:</>\t\t<white>{bool(response['message'].get('image'))}</>")

        # Iterate through dict, logging keys (now properly handling missing keys d/t PFP versioning differences across instances)
        for key in standard_keys:
            try:
                value = reduce(lambda x, k: x[k] if isinstance(x, dict) and k in x else None, key.split('.'), response)
                logger.opt(colors=True).log("RESPONSE", f"<cyan>{key}</>:\t<white>{value}</>")
            except KeyError:
                logger.opt(colors=True).log("RESPONSE", f"<cyan>{key}</>:\t<dim>Not present</>")

    except Exception as e:
        logger.error(f'Error logging API response keys: {e}')



## Generate summary report of latest batch of responses from target API...
def response_report(apiReturn):
    logger.debug("RUNNING FUNCITON: 'response_report'...")



## Auto-verification of vignette expectations against persona input_messages
def response_vign_verify(apiReturn, staffID):
    logger.debug("RUNNING FUNCTION: 'response_vign_verify'...")
    # Set up variables to parse through
    if args.pilotVerify:
        logger.info(f"Verifying against restricted pilot launch dataset")
        validKeys = pilotPairs.get(staffID)
    else:
        validKeys = vignAccPairs.get(staffID)
    selectedCPs = apiReturn["selected_candidate"].get("acceptable_by")
    selectedMeasure = apiReturn["selected_candidate"].get("measure")
    matchingCP = False
    matchingMeasure = False
    formattedValidKeys = [      # Make print statement pretty for valid pairs
        f"\t{item['acceptable_by'].title()}\t\t{item['measure']}" for item in validKeys
    ]
    # Error catcher for missing keys
    if not selectedCPs or not selectedMeasure:
        logger.warning("Selected candidate is missing 'acceptable_by' or 'measure'.")
        return
    
    # Check if any of the selected CPs match the valid CPs
    for selectedCP in selectedCPs:
        selectedCP = selectedCP.lower()
        for validKey in validKeys:
            if (
                selectedCP == validKey["acceptable_by"].lower()
                and selectedMeasure == validKey["measure"]
            ):
                matchingCP = selectedCP
                matchingMeasure = selectedMeasure
                break
    
    # Report results of verification
    if matchingCP and matchingMeasure:
        logger.info("VIGNETTE VERIFICATION:\t\tPASS")
        logger.info(f"Matched pair:\t\t{matchingCP.title()}\t\t{matchingMeasure}")
    else:
        logger.info("VIGNETTE VERIFICATION:\t\tFAIL")
        for formattedValidKey in formattedValidKeys:
            logger.info(f"Expected pairs:\t{formattedValidKey}")
        logger.info(f"API returned pair:\n\t\t{selectedCPs}\t\t{selectedMeasure}")



## Check output message against requested Causal Pathway...
def response_CP_verify(apiReturn, causalPathway):
    logger.debug("RUNNING FUNCTION: 'response_CP_verify'...")
    try:
        assert causalPathway is not None and isinstance(causalPathway, str), "Causal Pathway passed is not a valid string"
        assert apiReturn["selected_candidate"].get("acceptable_by") is not None, "No 'Acceptable By' keys returned by API"
    except AssertionError as e:
        logger.critical("Assertion error: " + str(e))
        return
    
    causalPathway = causalPathway.replace("_", " ")  # replace underscores of user input with spaces
    selectedCandidate = apiReturn["selected_candidate"]
    selectedCPList = selectedCandidate.get("acceptable_by")
    
    for selectedCP in selectedCPList:
        selectedCP = selectedCP.lower()
        if causalPathway == selectedCP:
            logger.info(f"CAUSAL PATHWAY VERIFICATION:\tPASS\n\t\tSpecified Pathway:\t{causalPathway}\n\t\tAccepted Pathway:\t{selectedCP}")
            logger.info(f"PFP returns acceptable candidates: {selectedCPList}\n")
            break
        else:
            logger.info(f"CAUSAL PATHWAY VERIFICATION:\tFAIL\n\t\tSpecified Pathway:\t{causalPathway}\n\t\tAccepted Pathway:\t{selectedCPList}")
            logger.info(f"No matching causal pathway found for '{causalPathway}'.\n")



## Save PFP API responses for manual review...
def save_API_resp(postReturn, requestID):
    logger.debug("RUNNING FUNCTION: 'save_API_resp'...")
    folderName = "APIResponseLogs"
    os.makedirs(folderName, exist_ok=True)

    texName = os.path.join(folderName, f"response_{requestID.lower()}.json")
    imgName = os.path.join(folderName, f"response_{requestID.lower()}.png")
    responseJson = postReturn.json()

    with open(texName, "w") as file:
        json.dump(responseJson, file, indent=2)
        logger.info(f"PFP response text saved to '{texName}'")
    
    with open(imgName, "wb") as imageFile:
        imageFile.write(base64.b64decode(responseJson["Message"]["image"]))
        logger.info(f"Pictoralist image saved to '{imgName}'.\n\n")



## Handle API responses (print resp, check response keys, save logs)...
def handle_response(response, requestID):
    logger.debug("RUNNING FUNCTION: 'handle_response'...")
    #logger.debug(f"Response Content: {response.content}")
    if response.status_code == 200:
        logger.info(f"{requestID}:\tResponse received in {response.elapsed.total_seconds():.3f} seconds.")
        apiReturn = response.json()
        staffID = apiReturn["staff_number"]
        
        if args.respond:    # Print output if asked
            log_response_subset(apiReturn)

        if args.vignVerify or args.pilotVerify:    # Validate vignette measure/causal pathway pair in output if asked
            response_vign_verify(apiReturn, staffID)

        if chkCP:       # Validate causal pathway output if asked
            response_CP_verify(apiReturn, args.CP)
            # not an ideal way to incorporate which causal pathway we want to assert, but workable
            
        if args.saveResponse:    # Save output if asked
            save_API_resp(response, requestID)

    else:
        logger.error("Bad response from target API:\n\t\t\tStatus Code:\t{!r}\nHeaders: {!r}\n{!r}".format(
        response.status_code, response.headers, response.text))





##### JSON Content Functions ###########################################################
### These functions handle where and how to read in JSON content to make valid post
### requests to the API.

## Fetch JSON content from GitHub... (V9)
def go_fetch(url):
    logger.debug("RUNNING FUNCTION: 'go_fetch'...")
    if "github.com" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob", "")
    header = {"Accept": "application/vnd.github.v3.raw"} # tell gitHub to send as raw, uncompressed
    bone = requests.get(url, headers=header)
    
    if bone.status_code == 200:
        try:
            jasonBone = json.dumps(json.loads(bone.text), indent=4) # reconstruct as JSON with indentation
            return jasonBone
        except json.JSONDecodeError as e:
            raise Exception("Failed parsing JSON content.")
    else:
        raise Exception(f"Failed to fetch JSON content from GitHub link: {url}")



## Read in CSV data from file, convert to JSON...
def csv_jsoner(path):
    logger.debug("RUNNING FUNCTION: 'csv_jsoner'...")
    # Adjust the 'usecols' parameter to skip the first column
    performance = pd.read_csv(path, header=None, usecols=range(args.CI, args.CF), skiprows=1, nrows=args.RF - args.RI)

    rowsRead, colsRead = performance.shape
    selectedRows = performance.iloc[args.RI: args.RF]
    jsonedData = ""

    # Integrated dimension error catcher:
    if colsRead != args.CF - args.CI or rowsRead != args.RF - args.RI:
        raise ValueError(f"Expected {args.RF - args.RI} rows and {args.CF - args.CI} columns. Actual data is {rowsRead} rows by {colsRead} columns.")

    # Integrated Dataframe to JSON conversion (V.15)
    for i, row in selectedRows.iterrows():
        currentLine = json.dumps(row.to_list())
        jsonedData += currentLine  # content addition
        if i < len(performance) - 1:
            jsonedData += ",\n\t"  # formatting
    return jsonedData






#### POST Functions ###################################################################
### Any and all functions that send a post request live here. Protected or unprotected,
### from any content source, and against any of the available API endpoints.

## Send POST request to unprotected URLs...
def send_post(pfp, fullMessage):
    logger.debug("RUNNING FUNCTION: 'send_unprotected_post'...")
    header = {"Content-Type": "application/json"}
    response = requests.post(pfp, data=fullMessage, headers=header)
    return response



## Send POST request to IAP protected URLs...
def send_iap_post(url, fullMessage, method="POST"):
    logger.debug("RUNNING FUNCTION:  'send_iap_post'...")
   
    # Check if token valid, refresh expired token if not
    if oidcToken.valid != True:
        request = google.auth.transport.requests.Request()
        oidcToken.refresh(request)

    # Fetch IAP-protected URL, auth header 'Bearer', and OpenID Connect token
    fullMessage=json.loads(fullMessage)
    resp = requests.post(
    url,
    headers={
        "Authorization": "Bearer {}".format(oidcToken.token),
        "Content-Type": "application/json",  # Set content-type to JSON
    },
    json=fullMessage,
    )
    logger.debug(f"bearer Token:\n{oidcToken.token}")
    return resp



## Send POST request (IAP or Unprotected), then handle response...
def post_and_respond(fullMessage, requestID):
    global pfp
    logger.debug("RUNNING FUNCTION: 'post_and_respond'...")
    try:
        if args.target != "cloud":
            sentPost = send_post(pfp, fullMessage)

        elif args.target == "cloud":
            sentPost = send_iap_post(pfp, fullMessage)

        handle_response(sentPost, requestID)
    
    except Exception as e:
        logger.critical(f"{e}")



## Test a knowledgebase repo input message JSON file...
def test_inputfile(mode, inputID, requestID):
    logger.debug("RUNNING FUNCTION: 'test_inputfile'...")
    try:
        if mode == "testIMs":   # Check if testing official persona input messages
            url = f"https://raw.githubusercontent.com/Display-Lab/knowledge-base/main/vignettes/personas/{inputID}/input_message.json"
            logger.info(f"\nTesting input_message file for persona '{inputID.upper()}'")

        elif mode == "testCPs": # Check if testing causal pathway suite input messages
            url = f"https://github.com/Display-Lab/knowledge-base/blob/main/vignettes/dev_templates/causal_pathway_test_suite/{inputID}_cptest.json"
            inputID = inputID.replace("_"," ")  # replace underscores with spaces
            logger.info(f"Testing input_message file for causal pathway '{inputID.upper()}'")
        
        jsonContent = go_fetch(url)     # retrieve github json content
        post_and_respond(jsonContent, requestID)

    except Exception as e:
        logger.critical(f"{e}")



## Automated full repo testing of all knowledgebase files...
def repo_test(mode, threadIndex, testIndex, requestID):
    logger.debug("RUNNING FUNCTION: 'repo_test'...")
    if mode == "testIMs":   # Run when testing persona input messages
        hitlist = hitlistIM
    elif mode == "testCPs": # Run when testing causal pathway input messages
        hitlist = hitlistCP
    
    for requestIndex, inputID in enumerate(hitlist, start=1):
        requestID = f"Thread {threadIndex}, Test {testIndex}, Request {requestIndex}" # add request index to ID
        args.CP = inputID     # Sneaky way to set current causal pathway from hitlist for verification
        test_inputfile(mode, inputID, requestID)



## Send local input_message files by user spec...
def send_locals(numberToSend, folderPath, requestID):
    logger.debug("RUNNING FUNCTION: 'send_locals'...")
    request_count = 0
    # Input message local files must be valid JSON files
    existing_files = [f for f in os.listdir(folderPath) if f.endswith(".json")]

    # Sort existing files numerically
    existing_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))

    # Take the desired number of files
    files_to_send = existing_files[:args.sendLocals]

    for file_name in files_to_send:
        request_count += 1
        if request_count % 6 == 0 and args.target == 'cloud':
            logger.info(f'Throttling requests for 30 seconds...')
            time.sleep(30)
        
        logger.debug(f'Attempting file: {file_name}')
        file_path = os.path.join(folderPath, file_name)
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                json_str = json.dumps(json_data, indent=2)  # Serialize with proper formatting
                post_and_respond(json_str, requestID)       # Send and respond to post request
        
        # Error catchers for debugging errors
        except json.decoder.JSONDecodeError as e:
            logger.warning(f"JSON decoding error in {file_name}: {e}")
        except Exception as e:
            logger.warning(f"Error reading {file_name}: {e}")




## Run POST requests while tracking thread number...
## Handles logic previously assigned to main script body
def run_requests(behavior, threadIndex, requestID, barrier): 
    logger.debug("RUNNING FUNCTION: 'run_requests'...")
    barrier.wait()  # Wait at barrier for all threads to be up
    try:
        for testIndex in range(args.tests):   # iterate through requested tests
            #logger.info(f"\nThread #{threadIndex+1}: Running test {testIndex+1} of {args.tests}:")
            requestID = f"Thread {threadIndex+1}, " # reset requestID
            requestID += f"Test {testIndex+1}, "   # add test # to response name
        
            # Run single-persona repo test
            if behavior == "onePers":
                requestID += f"Request 1"  # complete request name
                test_inputfile("testIMs", args.persona, requestID) # mode set to test persona input message

             # Run multi-persona repo test of persona input_message files
            elif behavior == "allPers":
                repo_test("testIMs", threadIndex+1, testIndex+1, requestID) # mode set to test persona input messages
            
            # Run single-causal pathway repo test
            if behavior == "oneCP":
                requestID += f"Request 1"  # complete request name
                test_inputfile("testCPs", args.CP, requestID) # mode set to test CP input message
            
            # Run multi-message test of causal pathway test suite
            elif behavior == "allCPs":
                repo_test("testCPs", threadIndex+1, testIndex+1, requestID) # mode set to test CP input messages
            
            # Retrieve specified GitHub payload and post
            elif behavior == "customGithub":
                requestID += f"Request 1"  # complete request name
                fullMessage = go_fetch(args.useGit)      # Retrieve GitHub payload
                post_and_respond(fullMessage, requestID)  # Send POST and respond
            
            # Build JSON payload from Addendum and post
            elif behavior == "postwoman":
                requestID += f"Request 1"  # complete request name
                perfJSON = postwoman
                fullMessage = payloadHeader + perfJSON + payloadFooter
                post_and_respond(fullMessage, requestID)

            # Build JSON payload from CSV file and post
            elif behavior == "CSV":
                requestID += f"Request 1"  # complete request name
                perfJSON = csv_jsoner(perfPath)
                fullMessage = payloadHeader + perfJSON + payloadFooter
                post_and_respond(fullMessage, requestID)
            
            # Send arbitrary local JSON input_message files
            elif behavior == 'sendLocals':
                requestID += f"Request 1"
                send_locals(args.sendLocals, "Local_inputs", requestID)

    except Exception as e:
        logger.critical(f"{e}")





# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########### Main Script Body ################################
def main():
    logger.success(f"\n\t\tWelcome to the Leakdown Tester, Version {ldtVersion}!")
    try:
        behavior = set_behavior()                                   # Set behavior
        calc_total_reqs(behavior)                                   # Calculate request number total
        set_target()                                                # Set API endpoint
        barrier = Barrier(args.threads)                             # Holds until all threads are up
        
        # Spawn and run threads 
        threads = []
        for threadIndex in range(args.threads):
            requestID = f"Thread {threadIndex + 1}, "   # First part of requesID name sequence
            thisThread = threading.Thread(
                target=run_requests,
                args=(behavior, threadIndex, requestID, barrier)
            )
            threads.append(thisThread)
            thisThread.start()
            logger.debug(f"\tThread #{threadIndex+1} started...")

        # Wait for threads to finish running
        for thisThread in threads:
            thisThread.join()

        logger.success("\t\t# LDT complete #\n\n")
        exit(0)


    except ValueError as e:
        logger.critical(f"{e}")
        exit(1)


if __name__ == "__main__":
    main()