import boto3
import json
import datetime
from pkg_resources import resource_filename

client = boto3.client('pricing', region_name='us-east-1')
# Search product filter. This will reduce the amount of data returned by the
# get_products function of the Pricing API
FLT = '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},' \
      '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},' \
      '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},' \
      '{{"Field": "instanceType", "Value": "{t}", "Type": "TERM_MATCH"}},' \
      '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
      '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'


# Get current AWS price for an on-demand instance
def get_price(region, instance, os='linux'):
    f = FLT.format(r=region, t=instance, o=os)
    data = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
    od = json.loads(data['PriceList'][0])['terms']['OnDemand']
    id1 = list(od)[0]
    id2 = list(od[id1]['priceDimensions'])[0]
    return od[id1]['priceDimensions'][id2]['pricePerUnit']['USD']


# Translate region code to region name. Even though the API data contains
# regionCode field, it will not return accurate data. However using the location
# field will, but then we need to translate the region code into a region name.
# You could skip this by using the region names in your code directly, but most
# other APIs are using the region code.
def get_region_name(region_code):
    default_region = 'US East (N. Virginia)'
    endpoint_file = resource_filename('botocore', 'data/endpoints.json')
    try:
        with open(endpoint_file, 'r') as f:
            data = json.load(f)
        # Botocore is using Europe while Pricing API using EU...sigh...
        return data['partitions'][0]['regions'][region_code]['description'].replace('Europe', 'EU')
    except IOError:
        return default_region


# Use AWS Pricing API through Boto3
# API only has us-east-1 and ap-south-1 as valid endpoints.
# It doesn't have any impact on your selected region for your instance.


def get_ondemand_price(region, instance_type):
    price = get_price(get_region_name(region), instance_type, 'linux')
    return price


def get_spot_price(region, az, instance_type):
    client = boto3.client('ec2', region_name=region)
    prices = client.describe_spot_price_history(
        InstanceTypes=[instance_type],
        ProductDescriptions=['Linux/UNIX', 'Linux/UNIX (Amazon VPC)'],
        StartTime=(datetime.datetime.now() -
                   datetime.timedelta(hours=1)).isoformat(),
        MaxResults=10
    )

    results = {}
    for price in prices["SpotPriceHistory"]:
        results[price["AvailabilityZone"]] = price["SpotPrice"]
    return results[az]


def get_node_price(capacity_type, region, az, instance_type):
    if capacity_type == 'SPOT':
        return eval(get_spot_price(region, az, instance_type))
    else:
        return eval(get_ondemand_price(region, instance_type))


if __name__ == '__main__':
    # Get current price for a given instance, region and os
    print(get_spot_price('us-east-1', 'us-east-1b', 'c5.xlarge'))

    print(type(get_ondemand_price('us-east-1', 'c5.xlarge')))
    print(type(get_node_price('SPOT', 'us-east-1', 'us-east-1b', 'c5.xlarge')))
