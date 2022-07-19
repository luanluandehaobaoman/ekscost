import os

# TIMESTREAM_REGION = "us-east-1"
# DATABASE_NAME = "ekscost"
# CLUSTER_NAME = "eks-dev"
# TABLE_POD = "pod_info"
# TABLE_NODE = "node_info"
# INTERVAL_POD = 15
# INTERVAL_NODE = 30

TIMESTREAM_REGION = os.getenv("TIMESTREAM_REGION") if os.getenv("TIMESTREAM_REGION") else "us-east-1"
DATABASE_NAME = os.getenv("DATABASE_NAME") if os.getenv("DATABASE_NAME") else "ekscost"
CLUSTER_NAME = os.getenv("CLUSTER_NAME") if os.getenv("CLUSTER_NAME") else "eks-dev"
TABLE_POD = os.getenv("TABLE_POD") if os.getenv("TABLE_POD") else "pod_info"
TABLE_NODE = os.getenv("TABLE_NODE") if os.getenv("TABLE_NODE") else "node_info"
INTERVAL_POD = os.getenv("INTERVAL_POD") if os.getenv("INTERVAL_POD") else 15
INTERVAL_NODE = os.getenv("INTERVAL_NODE") if os.getenv("INTERVAL_NODE") else 30

