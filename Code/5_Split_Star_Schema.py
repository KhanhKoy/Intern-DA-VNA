import pandas as pd
import numpy as np

def split_to_star_schema(master_filepath, output_dir):
    print("1. ĐANG ĐỌC FILE MASTER...")
    df = pd.read_csv(master_filepath)
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # -------------------------------------------------------------
    # 2. TẠO BẢNG Dim_Household_Status
    # -------------------------------------------------------------
    print("2. ĐANG TẠO BẢNG Dim_Household_Status...")
    dim_status = pd.DataFrame({
        'STATUS_ID': [0, 1, 2],
        'STATUS_NAME': ['Bình thường/Khác', 'Hộ nghèo', 'Hộ cận nghèo']
    })
    # Trong Fact table đổi cột PHAN_LOAI_HO thành STATUS_ID
    df = df.rename(columns={'PHAN_LOAI_HO': 'STATUS_ID'})
    # Ép kiểu nguyên cho an toàn
    df['STATUS_ID'] = df['STATUS_ID'].astype(int)
    dim_status.to_csv(f"{output_dir}/Dim_Household_Status.csv", index=False, encoding='utf-8-sig')

    # -------------------------------------------------------------
    # -------------------------------------------------------------
    # 3. TẠO BẢNG Dim_Demographic
    # -------------------------------------------------------------
    print("3. ĐANG TẠO BẢNG Dim_Demographic...")
    
    # BỔ SUNG: Dọn dẹp rác dạng Text (như 'ĐÃ CHẾT') trong cột Dân tộc
    # Dùng errors='coerce' để ép chữ thành NaN, sau đó fillna(1) để quy về dân tộc Kinh
    df['DANTOC_CHU_HO'] = pd.to_numeric(df['DANTOC_CHU_HO'], errors='coerce').fillna(1)
    
    REVERSE_DANTOC_MAP = {
        1: 'Kinh', 2: 'Tày', 3: 'Thái', 4: 'Hoa', 5: 'Khmer', 6: 'Mường', 7: 'Nùng', 
        8: 'Hmông', 9: 'Dao', 10: 'Gia Rai', 11: 'Ngái', 12: 'Ê Đê', 13: 'Ba Na', 
        14: 'Xơ Đăng', 15: 'Sán Chay', 16: 'Cơ Ho', 17: 'Chăm', 18: 'Sán Dìu', 19: 'Hrê', 
        20: 'M\'Nông', 21: 'Ra Glai', 22: 'Xtiêng', 23: 'Bru Vân Kiều', 24: 'Thổ', 
        25: 'Giáy', 26: 'Cơ Tu', 27: 'Giẻ Triêng', 28: 'Mạ', 29: 'Khơ Mú', 30: 'Co', 
        31: 'Tà Ôi', 32: 'Chơ Ro', 33: 'Kháng', 34: 'Xinh Mun'
    }
    
    # Lúc này ép kiểu int sẽ an toàn tuyệt đối
    unique_dantoc_codes = df['DANTOC_CHU_HO'].astype(int).unique()
    dim_demo_list = []
    for code in unique_dantoc_codes:
        name = REVERSE_DANTOC_MAP.get(code, "Khác")
        dim_demo_list.append({'DEMO_ID': code, 'DEMO_NAME': name})
        
    dim_demo = pd.DataFrame(dim_demo_list).sort_values('DEMO_ID')
    dim_demo.to_csv(f"{output_dir}/Dim_Demographic.csv", index=False, encoding='utf-8-sig')

    # -------------------------------------------------------------
    # 4. TẠO BẢNG Dim_Geography
    # -------------------------------------------------------------
    print("4. ĐANG TẠO BẢNG Dim_Geography...")
    # Lấy ra cặp Huyện - Xã độc nhất
    dim_geo = df[['HUYEN', 'XA']].drop_duplicates().reset_index(drop=True)
    # Tự sinh Geo_ID từ 1 trở đi (G1, G2...)
    dim_geo.insert(0, 'GEO_ID', ['G' + str(i+1) for i in range(len(dim_geo))])
    
    # Mapping ngược GEO_ID vào bảng Fact dựa trên cặp HUYEN-XA
    df = df.merge(dim_geo, on=['HUYEN', 'XA'], how='left')
    
    dim_geo.to_csv(f"{output_dir}/Dim_Geography.csv", index=False, encoding='utf-8-sig')

    # -------------------------------------------------------------
    # 5. TẠO BẢNG Fact_Household
    # -------------------------------------------------------------
    print("5. ĐANG TẠO BẢNG Fact_Household...")
    # Chỉ giữ lại các cột con số đo lường và Khóa ngoại (IDs)
    fact_columns = [
        'ID_HO_GLOBAL', 
        'QUY_MO_HO', 
        'LAO_DONG_CHINH', 
        'PHU_THUOC', 
        'TUOI_CHU_HO', 
        'GIOI_TINH_CHU_HO', # 1: Nam, 2: Nữ
        'STATUS_ID',        # FK trỏ về Dim_Status
        'DANTOC_CHU_HO',    # Được xem như DEMO_ID, trỏ về Dim_Demographic
        'GEO_ID'            # FK trỏ về Dim_Geography
    ]
    
    # Rename cột Dân tộc cho chuẩn naming convention của Foreign Key
    df_fact = df[fact_columns].rename(columns={'DANTOC_CHU_HO': 'DEMO_ID'})
    
    # Ép các cột thành Integer (ngoại trừ ID_HO_GLOBAL và GEO_ID là Text)
    int_cols = ['QUY_MO_HO', 'LAO_DONG_CHINH', 'PHU_THUOC', 'TUOI_CHU_HO', 'GIOI_TINH_CHU_HO', 'STATUS_ID', 'DEMO_ID']
    df_fact[int_cols] = df_fact[int_cols].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    
    df_fact.to_csv(f"{output_dir}/Fact_Household.csv", index=False, encoding='utf-8-sig')
    
    print(f"-> HOÀN TẤT TÁCH BẢNG! Mời bạn mở thư mục '{output_dir}' để kiểm tra 4 file CSV.")

if __name__ == "__main__":
    input_master = "DAK_NONG_HOUSEHOLDS_MASTER.csv" 
    output_directory = "Star_Schema_DB_Ready"
    
    split_to_star_schema(input_master, output_directory)