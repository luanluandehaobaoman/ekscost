from kubernetes import client, config
import get_ec2_price
import json

config.load_kube_config()


def get_node_info():
    v1 = client.CoreV1Api()
    nodes_data = {}
    nodes = v1.list_node()
    try:
        for node in nodes.items:
            node_name = node.metadata.name
            node_instance_type = node.metadata.labels['beta.kubernetes.io/instance-type']
            node_capacity_type = node.metadata.labels['eks.amazonaws.com/capacityType']
            node_zone = node.metadata.labels['topology.kubernetes.io/zone']
            node_region = node.metadata.labels['topology.kubernetes.io/region']
            node_allocatable_cpu = eval(node.status.allocatable['cpu'][0:-1])
            node_allocatable_memory = eval(node.status.allocatable['memory'][:-2]) / 1024
            node_price = get_ec2_price.get_node_price(node_capacity_type, node_region, node_zone, node_instance_type)
            node_resource = {
                'node_instance_type': node_instance_type,
                'node_capacityType': node_capacity_type,
                'node_zone': node_zone,
                'node_region': node_region,
                'node_allocatable_cpu': node_allocatable_cpu,
                'node_allocatable_memory': node_allocatable_memory,
                'node_price': node_price
            }
            nodes_data[node_name] = node_resource

        return nodes_data
    except Exception as err:
        print("Error:", err)


if __name__ == "__main__":
    i = get_node_info()
    print(json.dumps(i, indent=4))
