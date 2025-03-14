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
"r7g.large","r7g.xlarge","r7g.2xlarge","r7g.4xlarge","r7g.8xlarge","r7g.12xlarge","r7g.16xlarge","r6g.large","r6g.xlarge","r6g.2xlarge","r6g.4xlarge","r6g.8xlarge","r6g.12xlarge",
"r6g.16xlarge","r6i.large","r6i.xlarge","r6i.2xlarge","r6i.4xlarge","r6i.8xlarge","r6i.12xlarge","r6i.16xlarge","r6i.24xlarge","r6i.32xlarge","t3.nano",
"t3.micro","t3.small","t3.medium","t3.large","t3.xlarge","t3.2xlarge","r5.large","r5.xlarge","r5.2xlarge","r5.4xlarge","r5.8xlarge","r5.12xlarge","r5.16xlarge","r5.24xlarge",
"t4g.nano","t4g.micro","t4g.small","t4g.medium","t4g.large","t4g.xlarge","t4g.2xlarge"
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