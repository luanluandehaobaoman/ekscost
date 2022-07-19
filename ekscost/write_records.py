import time
import boto3
from botocore.config import Config
import get_pod_info
import get_node_info
from config import ekscost_config

session = boto3.Session()
write_client = session.client('timestream-write',
                              config=Config(read_timeout=20, max_pool_connections=5000,
                                            retries={'max_attempts': 10}), region_name=ekscost_config.TIMESTREAM_REGION)


def prepare_record(current_time, measure_name):
    record = {
        'Time': str(current_time),
        'MeasureName': measure_name,
        'MeasureValues': []
    }
    return record


def prepare_common_attributes(cluster_name):
    common_attributes = {
        'Dimensions': [
            {'Name': 'cluster', 'Value': cluster_name}
        ],
        'MeasureValueType': 'MULTI'
    }
    return common_attributes


def prepare_measure(measure_name, measure_value):
    if isinstance(measure_value, int):
        measure = {
            'Name': measure_name,
            'Value': str(measure_value),
            'Type': 'DOUBLE'
        }
        return measure
    elif isinstance(measure_value, float):
        measure = {
            'Name': measure_name,
            'Value': str(measure_value),
            'Type': 'DOUBLE'
        }
        return measure
    else:
        measure = {
            'Name': measure_name,
            'Value': str(measure_value),
            'Type': 'VARCHAR'
        }
        return measure


def write_records(records, common_attributes, db_name, table_name):
    try:

        result = write_client.write_records(DatabaseName=db_name,
                                            TableName=table_name,
                                            CommonAttributes=common_attributes,
                                            Records=records)
        status = result['ResponseMetadata']['HTTPStatusCode']
        print("%s Processed %d records. WriteRecords HTTPStatusCode: %s" %
              (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), len(records), status))
    except Exception as err:
        print("Error:", err)


def prepare_pods_records():
    try:
        pods_info = get_pod_info.get_pod_info()
        records = []
        for pod_name in pods_info:
            current_time = int(time.time() * 1000)
            # measure_name = "%s_%s" % (pods_info[pod_name]['pod_namespace'], pod_name)

            record = prepare_record(current_time, pod_name)
            # record['MeasureValues'].append(prepare_measure('pod_name', pod_name))
            record['MeasureValues'].append(prepare_measure('pod_request_cpu', pods_info[pod_name]['cpu_request']))
            record['MeasureValues'].append(prepare_measure('pod_request_memory', pods_info[pod_name]['memory_request']))
            record['MeasureValues'].append(prepare_measure('namespace', pods_info[pod_name]['pod_namespace']))
            record['MeasureValues'].append(prepare_measure('node_name', pods_info[pod_name]['pod_node_name']))
            record['MeasureValues'].append(
                prepare_measure('pod_utilization_cpu', pods_info[pod_name]['cpu_utilization']))
            record['MeasureValues'].append(
                prepare_measure('pod_utilization_memory', pods_info[pod_name]['memory_utilization']))

            records.append(record)
        return records
    except Exception as err:
        print("Error:", err)


def prepare_nodes_records():
    try:
        nodes_info = get_node_info.get_node_info()
        records = []
        for node_name in nodes_info:
            current_time = int(time.time() * 1000)

            record = prepare_record(current_time, node_name)
            record['MeasureValues'].append(
                prepare_measure('node_instance_type', nodes_info[node_name]['node_instance_type']))
            record['MeasureValues'].append(
                prepare_measure('node_capacityType', nodes_info[node_name]['node_capacityType']))
            record['MeasureValues'].append(prepare_measure('node_zone', nodes_info[node_name]['node_zone']))
            record['MeasureValues'].append(prepare_measure('node_region', nodes_info[node_name]['node_region']))
            record['MeasureValues'].append(
                prepare_measure('node_allocatable_cpu', nodes_info[node_name]['node_allocatable_cpu']))
            record['MeasureValues'].append(
                prepare_measure('node_allocatable_memory', nodes_info[node_name]['node_allocatable_memory']))
            record['MeasureValues'].append(prepare_measure('node_price', nodes_info[node_name]['node_price']))
            records.append(record)

        return records
    except Exception as err:
        print("Error:", err)


if __name__ == "__main__":
    pod_records = prepare_pods_records()
    write_client = session.client('timestream-write',
                                  config=Config(read_timeout=20, max_pool_connections=5000,
                                                retries={'max_attempts': 10}))

    common = prepare_common_attributes("eks-dev")
    write_records(pod_records, common, "ekscost", "dev_pod_info")
    node_records = prepare_nodes_records()
    write_records(node_records, common, db_name="ekscost", table_name="dev_node_info")
