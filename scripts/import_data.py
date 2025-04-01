import json
import os

def escape_sql_string(value):
    """Hàm để escape các ký tự đặc biệt trong chuỗi SQL."""
    if value is None:
        return 'NULL'
    # Xử lý chuỗi trước khi đưa vào f-string
    escaped_value = value.replace("'", "''")
    return f"'{escaped_value}'"

def generate_sql_from_json(json_file_path, sql_file_path):
    # Đọc file JSON
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Mở file SQL để ghi
    with open(sql_file_path, 'w', encoding='utf-8') as sql_file:
        # Ghi phần đầu của file SQL (tắt kiểm tra khóa ngoại để insert dễ dàng hơn)
        sql_file.write("SET FOREIGN_KEY_CHECKS=0;\n\n")

        # Duyệt qua từng tỉnh/thành phố
        for city_data in data:
            city_code = city_data['Code']
            city_name = city_data['FullName']
            print(f"Đang xử lý tỉnh/thành phố: {city_name}")

            # Ghi câu lệnh INSERT cho bảng city
            sql_file.write(
                f"INSERT INTO services_city (id, name) VALUES ({escape_sql_string(city_code)}, {escape_sql_string(city_name)});\n"
            )

            # Duyệt qua từng quận/huyện
            for district_data in city_data['District']:
                district_code = district_data['Code']
                district_name = district_data['FullName']
                city_code = district_data['ProvinceCode']

                # Ghi câu lệnh INSERT cho bảng district
                sql_file.write(
                    f"INSERT INTO services_district (id, name, city_id) VALUES ({escape_sql_string(district_code)}, {escape_sql_string(district_name)}, {escape_sql_string(city_code)});\n"
                )

                # Duyệt qua từng phường/xã
                if district_data['Ward']:
                    for ward_data in district_data['Ward']:
                        ward_code = ward_data['Code']
                        ward_name = ward_data['FullName']
                        district_code = ward_data['DistrictCode']

                        # Ghi câu lệnh INSERT cho bảng ward
                        sql_file.write(
                            f"INSERT INTO services_ward (id, name, district_id) VALUES ({escape_sql_string(ward_code)}, {escape_sql_string(ward_name)}, {escape_sql_string(district_code)});\n"
                        )
                else:
                    print(f"Không có phường/xã nào trong quận/huyện: {district_name} - {district_code}")

        # Ghi phần cuối của file SQL (bật lại kiểm tra khóa ngoại)
        sql_file.write("\nSET FOREIGN_KEY_CHECKS=1;\n")

    print(f"Đã tạo file SQL: {sql_file_path}")

if __name__ == "__main__":
    # Đường dẫn đến file JSON và file SQL (trên máy local)
    json_file_path = os.path.join(os.path.dirname(__file__), "vn_only_simplified_json_generated_data_vn_units.json")
    sql_file_path = os.path.join(os.path.dirname(__file__), "insert_data.sql")

    # Tạo file SQL từ JSON
    generate_sql_from_json(json_file_path, sql_file_path)