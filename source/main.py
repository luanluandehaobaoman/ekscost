import time
import boto3
import write_records
import ekscost_config

session = boto3.Session()
common_attributes = write_records.prepare_common_attributes(ekscost_config.CLUSTER_NAME)


def write_pod_records():
    pod_records = write_records.prepare_pods_records()
    # print(pod_records)
    write_records.write_records(pod_records, common_attributes, ekscost_config.DATABASE_NAME,
                                ekscost_config.TABLE_POD)


def write_node_records():
    node_records = write_records.prepare_nodes_records()
    # print(node_records)
    write_records.write_records(node_records, common_attributes, ekscost_config.DATABASE_NAME,
                                ekscost_config.TABLE_NODE)


while True:
    write_pod_records()
    write_node_records()

    time.sleep(15)

# threading.Thread(target=write_node_records()).start()
# threading.Thread(target=write_pod_records()).start()
