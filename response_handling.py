import os
import json
import base64
from loguru import logger
from functools import reduce
from settings import args, report_data
from LDT_Addendum import vignAccPairs, pilotPairs

#### API Response Handling #########################################################
### These functions print out response output, handle making logs of response output,
### and validate responses against known-good data (vignette specifications)


## Print subset of JSON keys from API response...
def log_response_subset(response):
    logger.opt(colors=True).trace("<dim>Running 'response_handling.log_response_subset'...</>")
    try:
        logger.opt(colors=True).log("RESPONSE", f"<b><c>API response contains keys:</></>")
        # Declare dict of keys in API response to log
        standard_keys = [
            'staff_number', 'message_instance_id', 'performance_month', 'selected_comparator',                  # 'Naked' keys
            'selected_candidate.display', 'selected_candidate.measure', 'selected_candidate.acceptable_by',     # Selected candidate keys
            'message.text_message'                                                                              # Message keys
        ]
        # Report image status vs returning full base64 key:
        logger.opt(colors=True).log("RESPONSE", f"<c>message.image:</>\t\t<white>{bool(response['message'].get('image'))}</>")

        # Iterate through dict, logging keys (now properly handling missing keys d/t PFP versioning differences across instances)
        for key in standard_keys:
            try:
                value = reduce(lambda x, k: x[k] if isinstance(x, dict) and k in x else None, key.split('.'), response)
                logger.opt(colors=True).log("RESPONSE", f"<c>{key}</>:\t<white>{value}</>")
            except KeyError:
                logger.opt(colors=True).log("RESPONSE", f"<c>{key}</>:\t<dim>Not present</>")

    except Exception as e:
        logger.error(f'Error logging API response keys: {e}')



## Auto-verification of vignette expectations against persona input_messages
def response_vign_verify(apiReturn, staffID):
    logger.opt(colors=True).trace("<dim>Running 'response_handling.response_vign_verify'...</>")
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
        logger.opt(colors=True).info("<g>Vignette Verification Passed</>")
        logger.info(f"Matched pair:\t\t{matchingCP.title()}\t\t{matchingMeasure}")
    else:
        logger.opt(colors=True).info("<r>Vignette Verification Failed</>")
        for formattedValidKey in formattedValidKeys:
            logger.info(f"Expected pairs:\t{formattedValidKey}")
        logger.info(f"API returned pair:\n\t\t{selectedCPs}\t\t{selectedMeasure}")



## Check output message against requested Causal Pathway...
def response_CP_verify(apiReturn, causalPathway):
    logger.opt(colors=True).trace("<dim>Running 'response_handling.response_CP_verify'...</>")
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
            logger.opt(colors=True).info("<g>Causal Pathway Verification Passed</>")
            logger.info(f"Specified Pathway:\t{causalPathway}\n\t\tAccepted Pathway:\t{selectedCP}")
            logger.info(f"PFP returns acceptable candidates: {selectedCPList}\n")
            break
        else:
            logger.opt(colors=True).info("<r>Causal Pathway Verification Failed</>")
            logger.info(f"Specified Pathway:\t{causalPathway}\n\t\tAccepted Pathway:\t{selectedCP}")
            logger.info(f"No matching causal pathway found for '{causalPathway}'.\n")



## Save PFP API responses for manual review...
def save_API_resp(postReturn, requestID):
    logger.opt(colors=True).trace("<dim>Running 'response_handling.save_API_resp'...</>")
    folderName = "APIResponseLogs"
    os.makedirs(folderName, exist_ok=True)

    texName = os.path.join(folderName, f"response_{requestID.lower()}.json")
    imgName = os.path.join(folderName, f"response_{requestID.lower()}.png")
    responseJson = postReturn.json()

    with open(texName, "w") as file:
        json.dump(responseJson, file, indent=2)
        logger.info(f"PFP response text saved to '{texName}'")
    
    with open(imgName, "wb") as imageFile:
        image_data = b''.join(responseJson['message']['image']) # rebuild image from list of bytes to full obj
        imageFile.write(base64.b64decode(image_data))
        logger.info(f"Pictoralist image saved to '{imgName}'.\n\n")



## Update summary dictionaries with template, pathway, and measures of each response...
def update_summary_dicts(response_json, report_data):
    logger.opt(colors=True).trace("<dim>Runnning 'response_handling.update_summary_dicts'...</>")
    if 'selected_candidate' in response_json:
        report_data.pathways.append(str(response_json['selected_candidate'].get('acceptable_by')))          # Add pathway to dict, cast as string
        report_data.measures.append(str(response_json['selected_candidate'].get('measure')))                # Add measure to dict as string
        report_data.templates.append(str(response_json['selected_candidate'].get('message_template_id')))   # Add message template ID as string


## Add summary text to log after all threads rejoin...
# no args as dicts are global if --report is used
def report_summary(report_data):
    logger.opt(colors=True).trace("<dim>Running 'response_handling.report_summary'...</>")
    logger.opt(colors=True).log('RESPONSE', f'\t<b><c>Response Summary Report</></>')
    report_matrix = [
        ('Message Templates', report_data.templates),
        ('Causal Pathways', report_data.pathways),
        ('Measures', report_data.measures),
    ]

    # Iterate through report matrix, generate report for each of the three dicts
    for dict_name, summary_dict in report_matrix:
        sum_dict_length = len(summary_dict)
        unique_items = set(summary_dict)  # Convert to a set to get unique items
        logger.opt(colors=True).log('RESPONSE', f'<c><u>{dict_name} were:</></>')
        
        # Iterate through unique strings in each of the three dicts, display how many of each string are in the overall summary dict
        for item in unique_items:
            item_count = summary_dict.count(item)  # Count occurrences of each unique item
            logger.opt(colors=True).log('RESPONSE', f'<c>{item}:</><white>\t{item_count}/{sum_dict_length}</>')




## Handle API responses (print resp, check response keys, save logs)...
def handle_response(response, requestID):
    logger.opt(colors=True).trace("<dim>Running 'response_handling.handle_response'...</>")
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
            update_summary_dicts(apiReturn, report_data)

    else:
        logger.error(
            "Bad response from target API:\n\t\t\tStatus Code:\t{!r}\nHeaders: {!r}\n{!r}".format(
            response.status_code, response.headers, response.text
        ))
