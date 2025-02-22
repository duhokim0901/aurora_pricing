import boto3
from datetime import datetime, timedelta

class AuroraClusterInfo:
    def __init__(self, profile_id, region, cmdb_role):
        self.profile_id = profile_id
        self.region = region
        self.cmdb_role = cmdb_role
        self.session = boto3.Session(profile_name=profile_id, region_name=region)
        self.rds_client = self.session.client("rds")

    def get_cluster_info(self):
        """cmdb_role 값과 일치하는 클러스터 정보를 반환"""
        clusters = self.rds_client.describe_db_clusters()["DBClusters"]
        matching_clusters = [
            cluster for cluster in clusters
            if any(tag["Key"] == "role" and tag["Value"] == self.cmdb_role for tag in cluster.get("TagList", []))
        ]
        return {cluster["DBClusterIdentifier"]: cluster for cluster in matching_clusters}

    def get_instance_list(self):
        """cmdb_role에 해당하는 클러스터 내 인스턴스 리스트 반환"""
        clusters = self.get_cluster_info()
        instance_dict = {}
        for cluster_id, cluster in clusters.items():
            instance_dict[cluster_id] = cluster["DBClusterMembers"]
        return instance_dict

    def get_cloudwatch_metrics(self, cluster_id, metric_name, period, start_time, end_time):
        """CloudWatch에서 클러스터 레벨의 메트릭을 조회"""
        cloudwatch = self.session.client("cloudwatch")
        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/RDS",
            MetricName=metric_name,
            Dimensions=[{"Name": "DBClusterIdentifier", "Value": cluster_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=["Average", "p90", "p95", "Maximum"]
        )

        metrics = response.get("Datapoints", [])
        return {dp["Timestamp"].isoformat(): {stat: dp[stat] for stat in ["Average", "Maximum"] if stat in dp} for dp in metrics}


class AuroraInstanceInfo:
    def __init__(self, profile_id, region, cmdb_role, instance_id=None):
        self.profile_id = profile_id
        self.region = region
        self.cmdb_role = cmdb_role
        self.instance_id = instance_id
        self.session = boto3.Session(profile_name=profile_id, region_name=region)
        self.rds_client = self.session.client("rds")

    def get_instance_info(self):
        """cmdb_role 값과 일치하는 인스턴스 정보를 반환 (특정 인스턴스 포함)"""
        clusters = AuroraClusterInfo(self.profile_id, self.region, self.cmdb_role).get_instance_list()
        instance_info = {}

        for cluster_id, instances in clusters.items():
            for instance in instances:
                if self.instance_id and instance["DBInstanceIdentifier"] != self.instance_id:
                    continue
                instance_info[instance["DBInstanceIdentifier"]] = instance
        return instance_info

    def get_cloudwatch_metrics(self, cluster_id, instance_id, metric_name, period, start_time, end_time):
        """CloudWatch에서 특정 인스턴스의 메트릭을 조회"""
        cloudwatch = self.session.client("cloudwatch")
        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/RDS",
            MetricName=metric_name,
            Dimensions=[{"Name": "DBInstanceIdentifier", "Value": instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=["Average", "p90", "p95", "Maximum"]
        )

        metrics = response.get("Datapoints", [])
        return {dp["Timestamp"].isoformat(): {stat: dp[stat] for stat in ["Average", "Maximum"] if stat in dp} for dp in metrics}
