from LDT_Addendum import payloadHeader, payloadFooter, ldtVersion, hitlistCP, hitlistIM, postwoman, pilotPairs
from post_functions import test_inputfile, repo_test, post_and_respond, send_locals
from response_handling import report_summary
from settings import args, report_data

from google.oauth2 import service_account
import google.auth.transport.requests
import threading
from threading import Barrier
from google.auth import crypt
from loguru import logger
import pandas as pd
import certifi
import base64
import json
import time
import os
import sys

#### Logging module configuration ######################################################
logger.remove()
log_level = args.loglvl.upper()  # Set log level

# Create unified sink with standard and custom log levels
logger.level("TRACE", color="<w>")
logger.level("RESPONSE", no=21, color="<c>")
logger.add(sys.stdout, level=log_level, format="<b><level>{level}</></> \t{message}")

# Save console log to file if asked
if args.saveLog:
    log_filename = 'Leakdown_Tests.log'  if args.saveLog   else None          
    logger.add(log_filename, level=log_level, format="<level>{level}</> \t| {message}")



##### Startup Functions ###############################################################
### Handle API endpoint, script behavior, and number of requests to send.
### V 0.4.3+ has integrated readback as configurations are set.

## Set script behavior for JSON content source (+ error handling and readback)...
def set_behavior():
    logger.opt(colors=True).trace("<dim>Running 'set_behavior'...</>")
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
    logger.opt(colors=True).trace("<dim>Running 'set_target'...</>")    
    
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
        args.oidcToken = service_account.IDTokenCredentials.from_service_account_file(
        args.SAPath,
        target_audience = args.audience,
        )
        logger.debug(f"Debug statements for GCP connection setup:\nTarget Audience:\n{args.audience}")
        logger.debug(f"Service Account Path:\n{args.SAPath}")
        logger.debug(f"OIDCToken:{args.oidcToken}")
    
    else:
        logger.warning("Target not declared. Continuing with local PFP target.")
    
    # Readback endpoint target when successfull
    logger.info(f"Sending POST request(s) to API at '{args.pfp}'...\n")



## Calculate total number of POST requests script will try to send...
def calc_total_reqs(behavior):
    logger.opt(colors=True).trace("<dim>Running 'calc_total_reqs'...</>")
    if behavior == "allPers":
        totalRequests = len(hitlistIM) * args.tests * args.threads
    if behavior == "allCPs":
        totalRequests = len(hitlistCP) * args.tests * args.threads
    else:
        totalRequests = args.tests * args.threads
    
    logger.info(f"Sending {totalRequests} total POST requests...")
    return totalRequests



## Read in CSV data from file, convert to JSON...
def csv_jsoner(path):
    logger.opt(colors=True).trace("<dim>Running 'csv_jsoner'...</>")
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




### Switchboard for choosing POST request mode while tracking thread number...
## Handles logic previously assigned to main script body - too bad python doesn't have switch cases
def run_requests(behavior, threadIndex, requestID, barrier): 
    logger.opt(colors=True).trace("<dim>Running 'run_requests'...</>")
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
            elif behavior == "oneCP":
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




########### Main Script Body ################################
def main():
    logger.opt(colors=True).success(f"\t<g><b><bg black>Welcome to the Leakdown Tester, Version {ldtVersion}!</></></>")
    try:
        behavior = set_behavior()                                   # Set behavior
        calc_total_reqs(behavior)                                   # Calculate request number total
        set_target()                                                # Set API endpoint                                        
        barrier = Barrier(args.threads)                             # Wait to start test until all threads are up
        
        # Spawn and run test threads 
        threads = []
        for threadIndex in range(args.threads):
            requestID = f"Thread {threadIndex + 1}, "   # First part of requesID name sequence
            thisThread = threading.Thread(
                target=run_requests,                    # Uses run_requests switchboard to specify tests to run in subprocess
                args=(behavior, threadIndex, requestID, barrier)
            )
            threads.append(thisThread)
            thisThread.start()
            logger.debug(f"\tThread #{threadIndex+1} started...")

        # Wait for threads to finish running
        for thisThread in threads: thisThread.join()

        # Output summary report if one was created for this test
        if args.report: report_summary(report_data)

        logger.opt(colors=True).success("\t <b><g><bg black>LDT complete</></></> \n\n\n")
        exit(0)


    except ValueError as e:
        logger.critical(f"{e}")
        exit(1)


if __name__ == "__main__":
    main()