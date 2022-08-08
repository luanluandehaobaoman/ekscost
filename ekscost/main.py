import time
import boto3
import write_records
from config import ekscost_config
import threading

session = boto3.Session()
common_attributes = write_records.prepare_common_attributes(ekscost_config.CLUSTER_NAME)


def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


def write_pod_records():
    pod_records = write_records.prepare_pods_records()
    group_pod_records = list_split(pod_records, 100)

    for i in group_pod_records:
        write_records.write_records(i, common_attributes, ekscost_config.DATABASE_NAME,
                                    ekscost_config.TABLE_POD)


def write_node_records():
    node_records = write_records.prepare_nodes_records()
    group_node_records = list_split(node_records, 100)
    for i in group_node_records:
        write_records.write_records(i, common_attributes, ekscost_config.DATABASE_NAME,
                                    ekscost_config.TABLE_NODE)


class WritePodRecords(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            write_pod_records()
            time.sleep(ekscost_config.INTERVAL_POD)


class WriteNodeRecords(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            write_node_records()
            time.sleep(ekscost_config.INTERVAL_NODE)


threads = []
threads.append(WritePodRecords())
threads[-1].start()
threads.append(WriteNodeRecords())
threads[-1].start()
