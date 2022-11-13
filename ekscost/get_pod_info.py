from kubernetes import client, config, dynamic
import json
from kubernetes.client import api_client

config.load_incluster_config()
# config.load_kube_config()

# list pod information and join metrics
def get_pod_info():
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    pods_data = {}
    pods_metrics = get_pod_metrics()
    for pod in pods.items:
        pod_name = pod.metadata.name
        pod_namespace = pod.metadata.namespace
        # measure_name = "%s_%s" % (pod_nsname, pod_name)
        pod_node_name = pod.spec.node_name
        if pod_name in pods_metrics:
            cpu_utilization = pods_metrics[pod_name]['cpu_util']
            memory_utilization = pods_metrics[pod_name]['memory_util']
        else:
            cpu_utilization = 0
            memory_utilization = 0
        pod_resource = {
            "cpu_request": 0,
            "memory_request": 0,
            "pod_namespace": pod_namespace,
            "pod_node_name": pod_node_name,
            "cpu_utilization": cpu_utilization,
            "memory_utilization": memory_utilization
        }
        for container in pod.spec.containers:
            requests = container.resources.requests
            if requests:
                cpu = requests.get("cpu", None)
                memory = requests.get("memory", None)
                if cpu:
                    if cpu[-1] == "m":
                        cpu = eval(cpu[0:-1])
                    else:
                        cpu = eval(cpu) * 1000
                    pod_resource["cpu_request"] += cpu
                if memory:
                    memory_mi = eval(memory[0:-2])
                    if memory[-2:] == "Gi":
                        memory_mi = memory_mi * 1024
                    elif memory[-2:] == "Mi":
                        memory_mi = memory_mi
                    elif memory[-2:] == "Ki":
                        memory_mi = memory_mi / 1024
                    else:
                        memory_mi = eval(memory) / 1024 / 1024
                    pod_resource["memory_request"] += memory_mi
            else:
                # print(pod_name, "requests not configured")
                break
        pods_data[pod_name] = pod_resource

    return pods_data


# get pod metrics from metrics server
def get_pod_metrics():
    # Creating a dynamic client
    dynamic_client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_incluster_config())
    )
    # dynamic_client = dynamic.DynamicClient(
    #     api_client.ApiClient(configuration=config.load_kube_config())
    # )
    # fetching the node api
    api = dynamic_client.resources.get(api_version="metrics.k8s.io/v1beta1", kind="PodMetrics")
    pod_data = {}
    for item in api.get().items:
        pod_name = item.metadata.name
        pod_utilization = {
            "cpu_util": 0,
            "memory_util": 0
        }
        for i in item.containers:
            cpu = i.usage.cpu
            memory = i.usage.memory
            if cpu:
                if cpu[-1] == "m":
                    cpu = eval(cpu[0:-1])
                elif cpu[-1] == "n":
                    cpu = eval(cpu[0:-1]) / 1000 / 1000
                elif cpu[-1] == "u":
                    cpu = eval(cpu[0:-1]) / 1000
                else:
                    cpu = eval(cpu) * 1000
                pod_utilization["cpu_util"] += cpu
            if memory:
                memory_mi = eval(memory[0:-2])
                if memory[-2:] == "Gi":
                    memory_mi = memory_mi * 1024
                elif memory[-2:] == "Mi":
                    memory_mi = memory_mi
                elif memory[-2:] == "Ki":
                    memory_mi = memory_mi / 1024
                else:
                    memory_mi = eval(memory) / 1024 / 1024
                pod_utilization["memory_util"] += memory_mi
        pod_data[pod_name] = pod_utilization
    return pod_data


if __name__ == "__main__":
    print(json.dumps(get_pod_info(), indent=4))
