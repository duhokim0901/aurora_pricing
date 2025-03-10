import boto3
import datetime
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_metric_data(cloudwatch, instance_id, metric_name, statistics, start_days, end_days):
    """클라우드워치에서 특정 Metric 데이터를 가져오는 함수"""
    now = datetime.datetime.utcnow()
    start_time = now + datetime.timedelta(days=start_days)
    end_time = now + datetime.timedelta(days=end_days)

    total_seconds = (end_time - start_time).total_seconds()
    period = max(60, round(total_seconds / 1440))  # 최소 60초
    period = period - (period % 60)  # 60의 배수로 조정

    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName=metric_name,
        Dimensions=[{"Name": "DBInstanceIdentifier", "Value": instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=statistics
    )

    # 데이터 정렬 및 값 추출
    data_points = sorted(response["Datapoints"], key=lambda x: x["Timestamp"])
    metric_data = {stat: [dp[stat] for dp in data_points] for stat in statistics}

    # 결과 저장
    metric_summary = {}
    for stat, values in metric_data.items():
        field_prefix = f"{metric_name}_{stat}_from{abs(start_days)}DaysAgo_to{abs(end_days)}DaysAgo"

        if values:
            metric_summary[f"{field_prefix}_p99"] = np.percentile(values, 99)
            metric_summary[f"{field_prefix}_p95"] = np.percentile(values, 95)
            metric_summary[f"{field_prefix}_max"] = max(values)
            metric_summary[f"{field_prefix}_min"] = min(values)
            metric_summary[f"{field_prefix}_mean"] = np.mean(values)
            metric_summary[f"{field_prefix}_sum"] = sum(values)
        else:
            metric_summary[f"{field_prefix}_p99"] = None
            metric_summary[f"{field_prefix}_p95"] = None
            metric_summary[f"{field_prefix}_max"] = None
            metric_summary[f"{field_prefix}_min"] = None
            metric_summary[f"{field_prefix}_mean"] = None
            metric_summary[f"{field_prefix}_sum"] = None

    return metric_summary

def get_aurora_metrics(profile_id, region, instance_id, metric_configs):
    """여러 개의 메트릭을 병렬로 가져오는 함수"""
    session = boto3.Session(profile_name=profile_id)
    cloudwatch = session.client('cloudwatch', region_name=region)

    results = {}

    # 병렬 처리로 메트릭 조회
    with ThreadPoolExecutor(max_workers=len(metric_configs)) as executor:
        future_to_metric = {
            executor.submit(fetch_metric_data, cloudwatch, instance_id, config["metric_name"], config["statistics"], config["start_days"], config["end_days"]): config["metric_name"]
            for config in metric_configs
        }

        for future in as_completed(future_to_metric):
            data = future.result()
            results.update(data)

    return results

# 사용 예제
profile_id = "your_aws_profile"
region = "ap-northeast-2"
instance_id = "your-aurora-instance"

# 각 메트릭별 start_days, end_days 개별 설정
metric_configs = [
    {"metric_name": "CPUUtilization", "statistics": ["Maximum", "Average"], "start_days": -30, "end_days": 0},
    {"metric_name": "FreeableMemory", "statistics": ["Maximum", "Average"], "start_days": -15, "end_days": -1},
    {"metric_name": "DatabaseConnections", "statistics": ["Maximum"], "start_days": -7, "end_days": -1}
]

result = get_aurora_metrics(profile_id, region, instance_id, metric_configs)
print(result)