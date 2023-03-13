## AWS Lambda function to process Shopify webhooks.
## If you want to use this function, you need to create a .env file with the following variables:
## META_ACCESS_TOKEN
## PIXEL_ID
## SHOPIFY_ACCESS_TOKEN
## TEST_EVENT_CODE

## Any suggestions or improvements are welcome! Feel free to contribute to this project or provide feedback.
import logging
import traceback
import time, datetime
import json
from dotenv import load_dotenv
import os
from requests import Response

def lambda_handler(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logging.debug(msg='funcall: lambda_handler')
    paylod = event.get('detail').get('payload')
    logging.info(msg='payload: ' + json.dumps(paylod, indent=4, sort_keys=True))

    try:
        response = main(paylod=paylod)
        logging.info(msg='response: ' + json.dumps(response, indent=4, sort_keys=True))
        return response

    except Exception as excp:
        traceback.print_exc()
        logging.error(excp)
        return {
            'statusCode': 400 if type(excp) == ValueError else 500,
            'body': 'event not sent: ' + str(excp) + ' ' + str(traceback.format_exc())
        }

def main(paylod) -> Response:
    '''
    Sends events to Google Ads
    '''
    for item in paylod.get('note_attributes'):
        if item["name"] == "gclidCookie":
            gclid = item["value"]

    if gclid == 'Not Found':
        gclid = None

    logging.debug('gclid: ' + str(gclid))

    ## GAds Purchase Event
    gads_response = send_event(
        conversion_action_id='6479384616',
        conversion_value=float(paylod.get('total_price')),
        gclid=gclid
    )

    if gads_response == True:
        logging.log('GAds event created')
    else:
        logging.error('GAds event not created')

    return gads_response

########### Core ###########
import hashlib
import os
import datetime

########### Google Ads ###########
from google.ads.googleads.client import GoogleAdsClient

########### Google Ads Conversions IDs ###########
'''
Purchase ctId=6479384616
'''

def send_event(
    conversion_action_id,
    conversion_value,
    gclid,
    conversion_custom_variable_id=None,
    conversion_custom_variable_value=None,
    gbraid=None,
    wbraid=None,
    customer_id='3340873698'
):
    """Creates a click conversion with a default currency of USD.

    Args:
        client: An initialized GoogleAdsClient instance.
        customer_id: The client customer ID string.
        conversion_action_id: The ID of the conversion action to upload to.
        gclid: The Google Click Identifier ID. If set, the wbraid and gbraid
            parameters must be None.
        conversion_date_time: The the date and time of the conversion (should be
            after the click time). The format is 'yyyy-mm-dd hh:mm:ss+|-hh:mm',
            e.g. '2021-01-01 12:32:45-08:00'.
        conversion_value: The conversion value in the desired currency.
        conversion_custom_variable_id: The ID of the conversion custom
            variable to associate with the upload.
        conversion_custom_variable_value: The str value of the conversion custom
            variable to associate with the upload.
        gbraid: The GBRAID for the iOS app conversion. If set, the gclid and
            wbraid parameters must be None.
        wbraid: The WBRAID for the iOS app conversion. If set, the gclid and
            gbraid parameters must be None.
    """
    # Google Ads  Service
    DEVELOPER_TOKEN = os.getenv('DEVELOPER_TOKEN')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
    ENV = os.getenv('ENV')

    #### Auth ####
    gds_auth = {
        'developer_token': DEVELOPER_TOKEN,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'login-customer-id':'3340873698',
        'use_proto_plus': True
    }
    # client = GoogleAdsClient.load_from_env()
    client = GoogleAdsClient.load_from_dict(config_dict=gds_auth)
    print('##### Google Ads client initiated #####')

    #### Datetime ####
    # 'yyyy-mm-dd hh:mm:ss+|-hh:mm', e.g. '2021-01-01 12:32:45-08:00'.
    conversion_date_time = datetime.datetime.now()


    if ENV == 'dev':
        format = "%Y-%m-%d %H:%M:%S-03:00"
        date_sting = conversion_date_time.strftime(format)
    elif ENV == 'prod' or 'test':
        gmt_minus_3 = conversion_date_time - datetime.timedelta(hours=3)
        format = "%Y-%m-%d %H:%M:%S-03:00"
        date_sting = gmt_minus_3.strftime(format)

    logging.debug(f'gads date string:{date_sting}')
    click_conversion = client.get_type("ClickConversion")
    conversion_action_service = client.get_service("ConversionActionService")
    click_conversion.conversion_action = (
        conversion_action_service.conversion_action_path(
            customer_id, conversion_action_id
        )
    )

    # Sets the single specified ID field.
    if gclid:
        click_conversion.gclid = gclid
    elif gbraid:
        click_conversion.gbraid = gbraid
    else:
        click_conversion.wbraid = wbraid

    click_conversion.conversion_value = float(conversion_value)
    click_conversion.conversion_date_time = date_sting
    click_conversion.currency_code = "BRL"

    if conversion_custom_variable_id and conversion_custom_variable_value:
        conversion_custom_variable = client.get_type("CustomVariable")
        conversion_custom_variable.conversion_custom_variable = (
            conversion_custom_variable_id
        )
        conversion_custom_variable.value = conversion_custom_variable_value
        click_conversion.custom_variables.append(conversion_custom_variable)

    conversion_upload_service = client.get_service("ConversionUploadService")
    request = client.get_type("UploadClickConversionsRequest")
    request.customer_id = customer_id
    request.conversions = [click_conversion]
    request.partial_failure = True
    conversion_upload_response = (
        conversion_upload_service.upload_click_conversions(
            request=request,
        )
    )
    partial_failure = is_partial_failure_error_present(conversion_upload_response)
    if partial_failure == True:
        print_results(client,conversion_upload_response)
        ## Returns false if contains errors
        return False
    uploaded_click_conversion = conversion_upload_response.results[0]
    print(
        f"Uploaded conversion that occurred at "
        f'"{uploaded_click_conversion.conversion_date_time}" from '
        f'Google Click ID "{uploaded_click_conversion.gclid}" '
        f'to "{uploaded_click_conversion.conversion_action}"'
    )

    ## Returns true if everything is ok
    return True

# def _normalize_and_hash_email_address(email_address):
#     """Returns the result of normalizing and hashing an email address.

#     For this use case, Google Ads requires removal of any '.' characters
#     preceding "gmail.com" or "googlemail.com"

#     Args:
#         email_address: An email address to normalize.

#     Returns:
#         A normalized (lowercase, removed whitespace) and SHA-265 hashed string.
#     """
#     normalized_email = email_address.lower()
#     email_parts = normalized_email.split("@")
#     # Checks whether the domain of the email address is either "gmail.com"
#     # or "googlemail.com". If this regex does not match then this statement
#     # will evaluate to None.
#     is_gmail = re.match(r"^(gmail|googlemail)\.com$", email_parts[1])

#     # Check that there are at least two segments and the second segment
#     # matches the above regex expression validating the email domain name.
#     if len(email_parts) > 1 and is_gmail:
#         # Removes any '.' characters from the portion of the email address
#         # before the domain if the domain is gmail.com or googlemail.com.
#         email_parts[0] = email_parts[0].replace(".", "")
#         normalized_email = "@".join(email_parts)

#     return _normalize_and_hash(normalized_email)

# def _normalize_and_hash(s):

#     """Normalizes and hashes a string with SHA-256.

#     Private customer data must be hashed during upload, as described at:
#     https://support.google.com/google-ads/answer/7474263

#     Args:
#         s: The string to perform this operation on.

#     Returns:
#         A normalized (lowercase, removed whitespace) and SHA-256 hashed string.
#     """
#     return hashlib.sha256(s.strip().lower().encode()).hexdigest()

def is_partial_failure_error_present(response):
    """Checks whether a response message has a partial failure error.

    In Python the partial_failure_error attr is always present on a response
    message and is represented by a google.rpc.Status message. So we can't
    simply check whether the field is present, we must check that the code is
    non-zero. Error codes are represented by the google.rpc.Code proto Enum:
    https://github.com/googleapis/googleapis/blob/master/google/rpc/code.proto

    Args:
        response:  A MutateAdGroupsResponse message instance.

    Returns: A boolean, whether or not the response message has a partial
        failure error.
    """
    partial_failure = getattr(response, "partial_failure_error", None)
    code = getattr(partial_failure, "code", None)
    return code != 0

def print_results(client, response):
    """Prints partial failure errors and success messages from a response.

    This function shows how to retrieve partial_failure errors from a response
    message (in the case of this example the message will be of type
    MutateAdGroupsResponse) and how to unpack those errors to GoogleAdsFailure
    instances. It also shows that a response with partial failures may still
    contain successful requests, and that those messages should be parsed
    separately. As an example, a GoogleAdsFailure object from this example will
    be structured similar to:

    error_code {
      range_error: TOO_LOW
    }
    message: "Too low."
    trigger {
      string_value: ""
    }
    location {
      field_path_elements {
        field_name: "operations"
        index {
          value: 1
        }
      }
      field_path_elements {
        field_name: "create"
      }
      field_path_elements {
        field_name: "campaign"
      }
    }

    Args:
        client: an initialized GoogleAdsClient.
        response: a MutateAdGroupsResponse instance.
    """
    # Check for existence of any partial failures in the response.
    if is_partial_failure_error_present(response):
        logging.warning("Partial failures occurred. Details will be shown below.\n")
        # Prints the details of the partial failure errors.
        partial_failure = getattr(response, "partial_failure_error", None)
        # partial_failure_error.details is a repeated field and iterable
        error_details = getattr(partial_failure, "details", [])

        for error_detail in error_details:
            # Retrieve an instance of the GoogleAdsFailure class from the client
            failure_message = client.get_type("GoogleAdsFailure")
            # Parse the string into a GoogleAdsFailure message instance.
            # To access class-only methods on the message we retrieve its type.
            GoogleAdsFailure = type(failure_message)
            failure_object = GoogleAdsFailure.deserialize(error_detail.value)

            for error in failure_object.errors:
                # Construct and print a string that details which element in
                # the above ad_group_operations list failed (by index number)
                # as well as the error message and error code.
                logging.warning(
                    "A partial failure at index "
                    f"{error.location.field_path_elements[0].index} occurred "
                    f"\nError message: {error.message}\nError code: "
                    f"{error.error_code}"
                )
    else:
        print(
            "All operations completed successfully. No partial failure "
            "to show."
        )

    # In the list of results, operations from the ad_group_operation list
    # that failed will be represented as empty messages. This loop detects
    # such empty messages and ignores them, while printing information about
    # successful operations.
    for message in response.results:
        if not message:
            continue

        print(f"Created ad group with resource_name: {message.resource_name}.")


