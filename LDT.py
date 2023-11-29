from LDT_Addendum import vignAccPairs, payloadHeader, payloadFooter, ldtVersion, hitlistCP, hitlistIM, postwoman, pilotPairs
from google.oauth2 import service_account
import google.auth.transport.requests
from dotenv import load_dotenv
import threading
from threading import Barrier
from google.auth import crypt
from functools import reduce
from settings import args
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
    logger.opt(colors=True).debug("<dim>Running 'set_behavior'...</>")
    # Error catcher for multiple JSON payload specification
    if args.perfCSVPath != None and args.useGit != None:
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
        logger.info(f"Reading data from CSV file at '{args.perfCSVPath}'...")
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
    global oidcToken
    logger.opt(colors=True).debug("<dim>Running 'set_target'...</>")    
    
    # Local API target:
    if args.target == "local":
        args.pfp = "http://127.0.0.1:8000/createprecisionfeedback/"
    
    # Heroku API target:
    elif args.target == "heroku":
        args.pfp = "https://pfpapi.herokuapp.com/createprecisionfeedback/"
    
    # GCP API target (ft. token retrieval):
    elif args.target == "cloud":
        assert args.audience, "Target Audience not set. Exiting..."
        assert args.SAPath, "Service Account Path not set. Exiting..."
        

        args.pfp = "https://pfp.test.app.med.umich.edu/createprecisionfeedback/"
        oidcToken = service_account.IDTokenCredentials.from_service_account_file(
        args.SAPath,
        target_audience = args.audience,
        )
        logger.debug(f"Debug statements for GCP connection setup:\nTarget Audience:\n{args.audience}")
        logger.debug(f"Service Account Path:\n{args.SAPath}")
        logger.debug(f"OIDCToken:{oidcToken}")
    
    else:
        logger.warning("Target not declared. Continuing with local PFP target.")
    
    # Readback endpoint target when successfull
    logger.info(f"Sending POST request(s) to API at '{args.pfp}'...\n")



## Calculate total number of POST requests script will try to send...
def calc_total_reqs(behavior):
    logger.opt(colors=True).debug("<dim>Running 'calc_total_reqs'...</>")
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
    logger.opt(colors=True).debug("<dim>Running 'log_response_subset'...</>")
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



## Auto-verification of vignette expectations against persona input_messages
def response_vign_verify(apiReturn, staffID):
    logger.opt(colors=True).debug("<dim>Running 'response_vign_verify'...</>")
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
    logger.opt(colors=True).debug("<dim>Running 'response_CP_verify'...</>")
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
    logger.opt(colors=True).debug("<dim>Running 'save_API_resp'...</>")
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



## Update summary dictionaries with template, pathway, and measures of each response...
def update_summary_dicts(response_json):
    logger.opt(colors=True).debug("<dim>Runnning 'update_summary_dicts'...</>")
    if 'selected_candidate' in response_json:
        pathway_sum_dict.append(str(response_json['selected_candidate'].get('acceptable_by')))      # Add pathway to dict, cast as string
        measures_sum_dict.append(str(response_json['selected_candidate'].get('measure')))           # Add measure to dict as string
        templates_sum_dict.append(str(response_json['selected_candidate'].get('message_template_id')))  # Add message template ID as string


## Add summary text to log after all threads rejoin...
# no args as dicts are global if --report is used
def report_summary():
    logger.opt(colors=True).log('RESPONSE', f'\t\t <b><cyan>Response Summary Report for this test:</></>\n')
    report_matrix = [
        ('Message Templates', templates_sum_dict),
        ('Causal Pathways', pathway_sum_dict),
        ('Measures', measures_sum_dict),
    ]

    # Iterate through report matrix, generate report for each of the three dicts
    for dict_name, summary_dict in report_matrix:
        sum_dict_length = len(summary_dict)
        unique_items = set(summary_dict)  # Convert to a set to get unique items
        logger.opt(colors=True).log('RESPONSE', f'<cyan>{dict_name} were:</>')
        
        # Iterate through unique strings in each of the three dicts, display how many of each string are in the overall summary dict
        for item in unique_items:
            item_count = summary_dict.count(item)  # Count occurrences of each unique item
            logger.opt(colors=True).log('RESPONSE', f'<cyan>{item}:</><white>\t{item_count}/{sum_dict_length}</>')




## Handle API responses (print resp, check response keys, save logs)...
def handle_response(response, requestID):
    logger.opt(colors=True).debug("<dim>Running 'handle_response'...</>")
    #logger.debug(f"Response Content: {response.content}")
    if response.status_code == 200:
        logger.info(f"{requestID}:\tResponse received in {response.elapsed.total_seconds():.3f} seconds.")
        apiReturn = response.json()
        staffID = apiReturn["staff_number"]
        
        if args.respond:    # Print output if asked
            log_response_subset(apiReturn)

        if args.vignVerify or args.pilotVerify:    # Validate vignette measure/causal pathway pair in output if asked
            response_vign_verify(apiReturn, staffID)

        if args.checkCP:       # Validate causal pathway output if asked
            response_CP_verify(apiReturn, args.CP)
            # not an ideal way to incorporate which causal pathway we want to assert, but workable
            
        if args.saveResponse:    # Save output if asked
            save_API_resp(response, requestID)

        if args.report:         # Update summary dicts when requested
            update_summary_dicts(apiReturn)

    else:
        logger.error("Bad response from target API:\n\t\t\tStatus Code:\t{!r}\nHeaders: {!r}\n{!r}".format(
        response.status_code, response.headers, response.text))





##### JSON Content Functions ###########################################################
### These functions handle where and how to read in JSON content to make valid post
### requests to the API.

## Fetch JSON content from GitHub... (V9)
def go_fetch(url):
    logger.opt(colors=True).debug("<dim>Running 'go_fetch'...</>")
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
    logger.opt(colors=True).debug("<dim>Running 'csv_jsoner'...</>")
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
    logger.opt(colors=True).debug("<dim>Running 'send_unprotected_post'...</>")
    header = {"Content-Type": "application/json"}
    response = requests.post(pfp, data=fullMessage, headers=header)
    return response



## Send POST request to IAP protected URLs...
def send_iap_post(url, fullMessage, method="POST"):
    logger.opt(colors=True).debug("<dim>Running  'send_iap_post'...</>")
   
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
    logger.opt(colors=True).debug("<dim>Running 'post_and_respond'...</>")
    try:
        if args.target != "cloud":
            response = send_post(args.pfp, fullMessage)

        elif args.target == "cloud":
            response = send_iap_post(args.pfp, fullMessage)
        
        # ALL requests go through handle_response (by design)
        handle_response(response, requestID)
    
    except Exception as e:
        logger.critical(f"{e}")



## Test a knowledgebase repo input message JSON file...
def test_inputfile(mode, inputID, requestID):
    logger.opt(colors=True).debug("<dim>Running 'test_inputfile'...</>")
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
    logger.opt(colors=True).debug("<dim>Running 'repo_test'...</>")
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
    logger.opt(colors=True).debug("<dim>Running 'send_locals'...</>")
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
    logger.opt(colors=True).debug("<dim>Running 'run_requests'...</>")
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
                perfJSON = csv_jsoner(args.perfCSVPath)
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
        
        # Initialize dictionaries for summary tracking while requests are sent
        if args.report:
            global templates_sum_dict, pathway_sum_dict, measures_sum_dict
            templates_sum_dict  = []
            pathway_sum_dict    = []
            measures_sum_dict   = []
        
        # Spawn and run test threads 
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
        for thisThread in threads: thisThread.join()

        if args.report: report_summary()

        logger.success("\t\t LDT complete \n\n")
        exit(0)


    except ValueError as e:
        logger.critical(f"{e}")
        exit(1)


if __name__ == "__main__":
    main()