import itertools
import csv

regions = ["ap-northeast-1", "ap-northeast-2", "ap-southeast-1"]
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