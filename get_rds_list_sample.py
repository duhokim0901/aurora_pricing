import boto3

client = boto3.client("rds")

def get_all_rds_instances():
    instances = []
    paginator = client.get_paginator("describe_db_instances")
    
    for page in paginator.paginate():
        instances.extend(page["DBInstances"])  # 각 페이지의 인스턴스 정보 추가
    
    return instances

rds_instances = get_all_rds_instances()
print(f"총 {len(rds_instances)} 개의 RDS 인스턴스를 가져왔습니다.")
for instance in rds_instances:
    print(instance["DBInstanceIdentifier"])
