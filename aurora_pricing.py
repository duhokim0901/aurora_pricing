import json
import subprocess

class AWSAuroraPricing:
    def __init__(self, database_engine=None, region=None, instance_type=None, model=None):
        self.database_engine = database_engine
        self.region = region
        self.instance_type = instance_type
        self.model = model
        self.filter_file = "filter.json"
        self.result_file = "result_filter.json"        
        self.volume_type = ""
        self.storage = ""    
        if self.model == "Standard" : 
            self.storage = "EBS Only" #EBS Only / Aurora IO Optimization Mode
            self.volume_type = "General Purpose-Aurora" #General Purpose-Aurora / IO Optimized-Aurora
        elif self.model == "IOOptimized" :
            self.storage = "Aurora IO Optimization Mode"
            self.volume_type = "IO Optimized-Aurora"                    

    #billing_type 은 Instance / IOUsage / EBSVoulme / IOOptimized 4가지로 분류함
    #model 이 Standard 일 경우 Instance, IOUsage, EBSVoulme 인 billing_type을 추출해야함
    #model 이 IOOptimized 일 경우 Instance, IOOptimized 인 billing_type을 추출해야함
    def create_filter_json(self, billing_type):
        """필터 JSON 파일 생성"""
        filter_data = []

        if billing_type == 'Instance':
            filter_data = [
                {"Type": "TERM_MATCH", "Field": "databaseEngine", "Value": self.database_engine},
                {"Type": "TERM_MATCH", "Field": "regionCode", "Value": self.region},
                {"Type": "TERM_MATCH", "Field": "productFamily", "Value": "Database Instance"},
                {"Type": "TERM_MATCH", "Field": "instanceType", "Value": self.instance_type},
                {"Type": "TERM_MATCH", "Field": "storage", "Value": self.storage}
            ]
        elif billing_type == 'EBSVoulme':
            if self.database_engine == "Aurora MySQL":
                filter_data = [
                    {"Type": "TERM_MATCH", "Field": "regionCode", "Value": self.region},
                    {"Type": "TERM_MATCH", "Field": "productFamily", "Value": "Database Storage"},
                    {"Type": "TERM_MATCH", "Field": "volumeType", "Value": self.volume_type},
                    {"Type": "TERM_MATCH", "Field": "databaseEngine", "Value": "Any"}
                ]
            else :
                filter_data = [
                    {"Type": "TERM_MATCH", "Field": "regionCode", "Value": self.region},
                    {"Type": "TERM_MATCH", "Field": "productFamily", "Value": "Database Storage"},
                    {"Type": "TERM_MATCH", "Field": "volumeType", "Value": self.volume_type},
                    {"Type": "TERM_MATCH", "Field": "databaseEngine", "Value": self.database_engine}
                ]                
        elif billing_type == 'IOOptimized':
            filter_data = [
                {"Type": "TERM_MATCH", "Field": "regionCode", "Value": self.region},
                {"Type": "TERM_MATCH", "Field": "productFamily", "Value": "Database Storage"},
                {"Type": "TERM_MATCH", "Field": "volumeType", "Value": self.volume_type},
                {"Type": "TERM_MATCH", "Field": "databaseEngine", "Value": self.database_engine}
            ]
        elif billing_type == 'IOUsage':
            if self.database_engine == "Aurora MySQL":
                filter_data = [
                    {"Type": "TERM_MATCH", "Field": "regionCode", "Value": self.region},
                    {"Type": "TERM_MATCH", "Field": "productFamily", "Value": "System Operation"},
                    {"Type": "TERM_MATCH", "Field": "groupDescription", "Value": "Input/Output Operation"},
                    {"Type": "TERM_MATCH", "Field": "group", "Value": "Aurora I/O Operation"},
                    {"Type": "TERM_MATCH", "Field": "databaseEngine", "Value": "Any"}
                ]
            else:
                filter_data = [
                    {"Type": "TERM_MATCH", "Field": "regionCode", "Value": self.region},
                    {"Type": "TERM_MATCH", "Field": "productFamily", "Value": "System Operation"},
                    {"Type": "TERM_MATCH", "Field": "groupDescription", "Value": "Input/Output Operation"},
                    {"Type": "TERM_MATCH", "Field": "group", "Value": "Aurora I/O Operation"},
                    {"Type": "TERM_MATCH", "Field": "databaseEngine", "Value": self.database_engine}
                ]


        with open(self.filter_file, "w") as f:
            json.dump(filter_data, f, indent=2)


    def extract_pricing_info(self, pricing_data):        
        """AWS JSON 데이터에서 가격 정보 추출"""
        try:
            unit = ''
            price_per_unit = ''
            
            #print(pricing_data["PriceList"][0])
            
            # PriceList가 문자열로 감싸져 있는 경우 JSON 변환
            price_list = json.loads(pricing_data["PriceList"][0])
            
            # OnDemand 가격 정보 가져오기 (동적으로 키 탐색)
            on_demand_terms = price_list["terms"]["OnDemand"]
            on_demand_key = next(iter(on_demand_terms))  # 첫 번째 키 찾기

            price_dimensions = on_demand_terms[on_demand_key]["priceDimensions"]
            price_dimension_key = next(iter(price_dimensions))  # 첫 번째 키 찾기
            
            unit = price_dimensions[price_dimension_key]["unit"]
            price_per_unit = price_dimensions[price_dimension_key]["pricePerUnit"]["USD"]

            return {
                "unit": unit,
                "price_per_unit": price_per_unit
            }

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"[-] JSON 파싱 오류: {e}")
            return None


    def get_aurora_pricing(self):
        pricing_result = []
        
        if self.model == "Standard":
                                         
            try:
                #빌링 타입별 필터조건 생성
                #빌링 타입 : Instance
                billing_type = "Instance" #Instance / IOUsage / EBSVoulme
                self.create_filter_json(billing_type)                
                
                command = [
                    "aws", "pricing", "get-products",
                    "--service-code", "AmazonRDS",
                    "--region", "us-east-1",
                    "--filters", f"file://{self.filter_file}"
                ]

                result = subprocess.run(command, capture_output=True, text=True, check=True)

                with open(self.result_file, "w") as f:
                    f.write(result.stdout)

                pricing_data = json.loads(result.stdout)
                extract_pricing_data = self.extract_pricing_info(pricing_data)
                
                if extract_pricing_data is None:
                    extract_pricing_data = {"unit": "N/A", "price_per_unit": "N/A"} #기본값 설정

                result_dict = { "database_engine" : self.database_engine,
                               "region" : self.region,
                               "instance_type" : self.instance_type,
                               "model" : self.model,
                               "billing_type" : billing_type,
                               "unit" : extract_pricing_data['unit'],
                               "price_per_unit" : extract_pricing_data['price_per_unit']
                }  
                
                pricing_result.append(result_dict)            


                #빌링 타입 : EBSVoulme
                billing_type = "EBSVoulme" #Instance / IOUsage / EBSVoulme
                self.create_filter_json(billing_type)                
                
                command = [
                    "aws", "pricing", "get-products",
                    "--service-code", "AmazonRDS",
                    "--region", "us-east-1",
                    "--filters", f"file://{self.filter_file}"
                ]

                result = subprocess.run(command, capture_output=True, text=True, check=True)

                with open(self.result_file, "w") as f:
                    f.write(result.stdout)

                pricing_data = json.loads(result.stdout)
                extract_pricing_data = self.extract_pricing_info(pricing_data)

                if extract_pricing_data is None:
                    extract_pricing_data = {"unit": "N/A", "price_per_unit": "N/A"} #기본값 설정

                result_dict = { "database_engine" : self.database_engine,
                               "region" : self.region,
                               "instance_type" : self.instance_type,
                               "model" : self.model,
                               "billing_type" : billing_type,
                               "unit" : extract_pricing_data['unit'],
                               "price_per_unit" : extract_pricing_data['price_per_unit']
                }  
                
                pricing_result.append(result_dict)


                #빌링 타입 : IOUsage
                billing_type = "IOUsage" #Instance / IOUsage / EBSVoulme
                self.create_filter_json(billing_type)                
                
                command = [
                    "aws", "pricing", "get-products",
                    "--service-code", "AmazonRDS",
                    "--region", "us-east-1",
                    "--filters", f"file://{self.filter_file}"
                ]

                result = subprocess.run(command, capture_output=True, text=True, check=True)

                with open(self.result_file, "w") as f:
                    f.write(result.stdout)

                pricing_data = json.loads(result.stdout)
                extract_pricing_data = self.extract_pricing_info(pricing_data)

                if extract_pricing_data is None:
                    extract_pricing_data = {"unit": "N/A", "price_per_unit": "N/A"} #기본값 설정

                result_dict = { "database_engine" : self.database_engine,
                               "region" : self.region,
                               "instance_type" : self.instance_type,
                               "model" : self.model,
                               "billing_type" : billing_type,
                               "unit" : extract_pricing_data['unit'],
                               "price_per_unit" : extract_pricing_data['price_per_unit']
                }  
                
                pricing_result.append(result_dict)

                return pricing_result

            except subprocess.CalledProcessError as e:
                print(f"[-] AWS CLI 실행 오류: {e}")
                return None
        
        elif self.model == "IOOptimized":                           
            try:
                #빌링 타입별 필터조건 생성
                #빌링 타입 : Instance
                billing_type = "Instance" #Instance / IOOptimized  
                self.create_filter_json(billing_type)
                command = [
                    "aws", "pricing", "get-products",
                    "--service-code", "AmazonRDS",
                    "--region", "us-east-1",
                    "--filters", f"file://{self.filter_file}"
                ]

                result = subprocess.run(command, capture_output=True, text=True, check=True)

                with open(self.result_file, "w") as f:
                    f.write(result.stdout)

                pricing_data = json.loads(result.stdout)
                extract_pricing_data = self.extract_pricing_info(pricing_data)

                if extract_pricing_data is None:
                    extract_pricing_data = {"unit": "N/A", "price_per_unit": "N/A"} #기본값 설정

                result_dict = { "database_engine" : self.database_engine,
                               "region" : self.region,
                               "instance_type" : self.instance_type,
                               "model" : self.model,
                               "billing_type" : billing_type,
                               "unit" : extract_pricing_data['unit'],
                               "price_per_unit" : extract_pricing_data['price_per_unit']
                }  
                
                pricing_result.append(result_dict)            

                #빌링 타입 : IOOptimized
                billing_type = "IOOptimized" #Instance / IOOptimized  
                self.create_filter_json(billing_type)
                command = [
                    "aws", "pricing", "get-products",
                    "--service-code", "AmazonRDS",
                    "--region", "us-east-1",
                    "--filters", f"file://{self.filter_file}"
                ]

                result = subprocess.run(command, capture_output=True, text=True, check=True)

                with open(self.result_file, "w") as f:
                    f.write(result.stdout)

                pricing_data = json.loads(result.stdout)
                extract_pricing_data = self.extract_pricing_info(pricing_data)

                if extract_pricing_data is None:
                    extract_pricing_data = {"unit": "N/A", "price_per_unit": "N/A"} #기본값 설정

                result_dict = { "database_engine" : self.database_engine,
                               "region" : self.region,
                               "instance_type" : self.instance_type,
                               "model" : self.model,
                               "billing_type" : billing_type,
                               "unit" : extract_pricing_data['unit'],
                               "price_per_unit" : extract_pricing_data['price_per_unit']
                }  
                
                pricing_result.append(result_dict)  
                                
                return pricing_result

            except subprocess.CalledProcessError as e:
                print(f"[-] AWS CLI 실행 오류: {e}")
                return None
        
        return pricing_result
    

if __name__ == "__main__":
    region = "ap-south-2" #ap-northeast-2 / ap-northeast-1 / us-east-1
    instance_type = "db.r6i.32xlarge"  
    database_engine = "Aurora PostgreSQL" #Aurora MySQL / Aurora PostgreSQL
    model = "Standard" #Standard / IOOptimized
    
    aurora_pricing = AWSAuroraPricing(database_engine=database_engine, region=region, instance_type=instance_type, model=model)
    pricing_data = aurora_pricing.get_aurora_pricing()
    if pricing_data:
        print("[+] 볼륨 가격 데이터 추출 완료")
        for price in pricing_data:
            print(price)
    else:
        print("[-] 볼륨 가격 데이터를 찾을 수 없음")
