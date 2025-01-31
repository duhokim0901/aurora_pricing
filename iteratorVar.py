import itertools
import csv

regions = ["us-east-1","us-east-2","us-west-1","us-west-2","af-south-1","ap-east-1",
"ap-south-2","ap-southeast-3","ap-southeast-4","ap-southeast-5","ap-south-1",
"ap-northeast-3","ap-northeast-2","ap-southeast-1","ap-southeast-2",
"ap-northeast-1","ca-central-1","ca-west-1","eu-central-1","eu-west-1",
"eu-west-2","eu-south-1","eu-west-3","eu-south-2","eu-north-1","eu-central-2",
"il-central-1","me-south-1","me-central-1","sa-east-1"]

instance_types = [
    "db.r6i.large", "db.r6i.xlarge", "db.r6i.2xlarge", "db.r6i.4xlarge",
    "db.r6i.8xlarge", "db.r6i.12xlarge", "db.r6i.16xlarge", "db.r6i.24xlarge", "db.r6i.32xlarge"
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