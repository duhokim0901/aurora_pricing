import itertools
import csv

#regions = ["us-east-1","us-east-2","us-west-1","us-west-2","af-south-1","ap-east-1",
#"ap-south-2","ap-southeast-3","ap-southeast-4","ap-southeast-5","ap-south-1",
#"ap-northeast-3","ap-northeast-2","ap-southeast-1","ap-southeast-2",
#"ap-northeast-1","ca-central-1","ca-west-1","eu-central-1","eu-west-1",
#"eu-west-2","eu-south-1","eu-west-3","eu-south-2","eu-north-1","eu-central-2",
#"il-central-1","me-south-1","me-central-1","sa-east-1"]

regions = ["ap-northeast-1","ap-northeast-2","ap-northeast-3"]

#r5, r6i, r6g, t3, t4g, r7
instance_types = [
    "db.t4g.micro","db.t4g.small","db.t4g.medium","db.t4g.large","db.t4g.xlarge","db.t4g.2xlarge",
    "db.t3.micro","db.t3.small","db.t3.medium","db.t3.large","db.t3.xlarge","db.t3.2xlarge","db.r5.large",
    "db.r5.xlarge","db.r5.2xlarge","db.r5.4xlarge","db.r5.8xlarge","db.r5.12xlarge","db.r5.16xlarge",
    "db.r5.24xlarge","db.r6i.large","db.r6i.xlarge","db.r6i.2xlarge","db.r6i.4xlarge","db.r6i.8xlarge",
    "db.r6i.12xlarge","db.r6i.16xlarge","db.r6i.24xlarge","db.r6i.32xlarge","db.r6g.large","db.r6g.xlarge",
    "db.r6g.2xlarge","db.r6g.4xlarge","db.r6g.8xlarge","db.r6g.12xlarge","db.r6g.16xlarge","db.r7g.large",
    "db.r7g.xlarge","db.r7g.2xlarge","db.r7g.4xlarge","db.r7g.8xlarge","db.r7g.12xlarge","db.r7g.16xlarge",
    "db.r7i.large","db.r7i.xlarge","db.r7i.2xlarge","db.r7i.4xlarge","db.r7i.8xlarge","db.r7i.12xlarge","db.r7i.16xlarge",
    
]
database_engines = ["Aurora MySQL", "Aurora PostgreSQL"]
models = ["Standard", "IOOptimized"]

# 모든 조합 생성
combinations = itertools.product(regions, instance_types, database_engines, models)

# CSV 파일로 저장
csv_filename = "aws_combinations.csv"
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Region", "Instance Type", "Database Engine", "Model"])  # 헤더
    writer.writerows(combinations)

print(f"CSV 파일이 생성되었습니다: {csv_filename}")