import csv
from aurora_pricing import AWSAuroraPricing

if __name__ == "__main__":
    # 입력 CSV 파일과 출력 CSV 파일
    input_csv = "aws_combinations.csv"
    output_csv = "aurora_pricing_output.csv"

    # 파일 읽기 및 실행
    with open(input_csv, mode="r", newline="") as infile, open(output_csv, mode="w", newline="") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # 첫 번째 줄(헤더) 읽기
        header = next(reader)
        
        # 아웃풋에 헤더 생성
        writer.writerow(header + ["Instance(Hrs)","Disk(GB-Mo)","IOUsage(IOs)"])  # 결과 CSV에 'Pricing' 추가

        # 각 조합 실행 후 결과 저장
        for row in reader:
            region, instance_type, database_engine, model = row            
            aurora_pricing = AWSAuroraPricing(database_engine=database_engine, region=region, instance_type=instance_type, model=model)            
            pricing_data = aurora_pricing.get_aurora_pricing()
            
            instance = 0
            disk = 0
            iops = 0
            
            for price in pricing_data:
                if price['billing_type'] == 'Instance':
                    instance = price['price_per_unit']
                elif price['billing_type'] == 'EBSVoulme' or price['billing_type'] == 'IOOptimized':
                    disk = price['price_per_unit']
                if price['billing_type'] == 'IOUsage':
                    iops = price['price_per_unit']
            
            writer.writerow(row + [instance,disk,iops])

    print(f"결과 CSV 파일 생성: {output_csv}")
