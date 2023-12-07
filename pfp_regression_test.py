import subprocess
import sys
import os
import pytest
from loguru import logger

#### Basal Functions for All Verification Tests  ######################################################
logger.remove()     # comment out for higher trace specificity than loglvl trace provides
logger.add(sys.stdout, level='INFO', format="<b><level>{level}</></> \t{message}")


## Run any generic LDT test and capture output
def run_ldt(ldt_command):
    logger.trace('Running run_ldt()...')
    # Runs LDT as a subprocess
    result = subprocess.run(ldt_command, capture_output=True, text=True, shell=True)
    return result.stdout


## Strip LDT log apart and parse as JSON to search through for keys to match on
def strip_ldt_log(log):
    logger.trace('Running strip_ldt_log()...')
    try:
        # Find the position of the last common trace line for all successful requests
        start_position = log.find("TRACE 	Running 'response_handling.handle_response'...")

        # Extract the relevant part of the output (from the common trace line to the end)
        response_json = log[start_position:].strip()
        return response_json
    
    # Error handlers
    except ValueError as json_error:
        logger.error(f"Error decoding JSON: {json_error}")
        return None

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
#######################################################################################################

## Test a generic causal pathway's functionality
def causal_pathway_test_framework(pathway, measure, acceptable_by):
    logger.trace(f'Running causal_pathway_test for {pathway}...')
    ldt_command = f"python3 ldt.py --loglvl trace --target local --CP {pathway} --respond"
    
    test_output = run_ldt(ldt_command)
    logger.debug('LDT subprocess finished')

    # Call func to strip end of response log to use for expeced outcome matching
    output_data = strip_ldt_log(test_output)

    ## Assert expected outcome is being seen in output
    if output_data != None:
        logger.debug(output_data)
        assert f"selected_candidate.measure:	{measure}" in output_data
        assert f"selected_candidate.acceptable_by:	['{acceptable_by}']" in output_data
 
    else:
        logger.error("An error occured. Verification could not be completed.") 


    
## Test student_t_cleaner functionality
def cleaner_test():
    logger.trace('Running cleaner_test...')
    ldt_command = "python3 ldt.py --loglvl trace --target local --sendLocals 1 --localPath Regression_tests/PFP/no-significant-data.json"
    
    test_output = run_ldt(ldt_command)
    logger.debug('LDT subprocess finished')

    # Call func to strip end of response log to use for expeced outcome matching
    output_data = strip_ldt_log(test_output)

    ## Assert expected outcome is being seen in output
    if output_data != None:
        logger.debug(output_data)
        assert 'detail' in output_data
        assert '400-error' in output_data
        assert 'Status Code:	400' in output_data
 
    else:
        logger.error("An error occured. Verification could not be completed.")



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
### Code to paramterize test cases for pytest automation ###
# After installing pytest-^7.4.3, run all test using `pytest -sv pfp_regression_test.py``

@pytest.mark.parametrize("pathway, measure, acceptable_by", [
    # Active causal pathway test cases:
    ('social_worse', 'GLU01', 'Social Worse'),
    ('social_better', 'SUS04', 'Social better'),
    ('improving', 'BP03', 'Improving'),
])
def test_causal_pathway(pathway, measure, acceptable_by):
    causal_pathway_test_framework(pathway, measure, acceptable_by)

def test_cleaner():
    cleaner_test()

if __name__ == "__main__":
    pytest.main(["-sv", "pfp_regression_test.py"])