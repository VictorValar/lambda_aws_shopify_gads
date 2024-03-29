########### Google Ads ###########
from google.ads.googleads.client import GoogleAdsClient
import os

# Google Ads  Service
DEVELOPER_TOKEN = os.getenv('DEVELOPER_TOKEN')
CLIENT_CUSTOMER_ID = os.getenv('CLIENT_CUSTOMER_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')

#### Auth ####
gds_auth = {
        'developer_token': DEVELOPER_TOKEN,
        'CLIENT_CUSTOMER_ID': CLIENT_CUSTOMER_ID,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'use_proto_plus': True
    }

# client = GoogleAdsClient.load_from_env()
client = GoogleAdsClient.load_from_dict(config_dict=gds_auth)
print('##### Google Ads client initiated #####')


### Get custom var ids and names ####
googleads_service = client.get_service("GoogleAdsService")

query = f"""SELECT conversion_action.id, conversion_action.name, metrics.all_conversions, metrics.all_conversions_value, metrics.conversion_last_conversion_date FROM conversion_action"""

search_request = client.get_type("SearchGoogleAdsRequest")
search_request.customer_id = CLIENT_CUSTOMER_ID
search_request.query = query
search_request.page_size = 100
results = googleads_service.search(request=search_request)
for row in results:
    if row.conversion_action.name in ['Purchase']:
        print(row)

