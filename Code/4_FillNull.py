import pandas as pd
import glob
import numpy as np

def prepare_final_dataset(input_folder, output_filepath):
    print("1. ĐANG GỘP 8 FILE HỘ GIA ĐÌNH...")
    files = glob.glob(input_folder + "/*_HOUSEHOLD.xlsx")
    df_all = pd.concat([pd.read_excel(f) for f in files], ignore_index=True)
    
    print("2. ĐANG ĐIỀN KHUYẾT (IMPUTATION) DỮ LIỆU BỊ TRỐNG...")
    # 2.1 Xử lý phân loại hộ: Trống (NaN) nghĩa là Hộ Bình Thường/Đã thoát nghèo -> Điền số 0
    df_all['PHAN_LOAI_HO'] = df_all['PHAN_LOAI_HO'].fillna(0)
    
    # 2.2 Xử lý Huyện/Xã: Nếu trống thì nội suy (Forward fill) hoặc lấy từ tiền tố ID
    # VD: ID là 'CJ_123' thì chắc chắn Huyện là Cư Jút
    prefix_to_huyen = {
        'CJ': 'CƯ JUT', 'DM': 'ĐĂK MIL', 'DGL': 'ĐẮK GLONG', 
        'DRL': 'ĐẮK RLẤP', 'DS': 'ĐẮK SONG', 'KN': 'KRÔNG NÔ', 
        'TD': 'TUY ĐỨC', 'GN': 'GIA NGHĨA'
    }
    df_all['TEMP_PREFIX'] = df_all['ID_HO_GLOBAL'].str.extract(r'^([A-Z]+)_')[0]
    df_all['HUYEN'] = df_all['HUYEN'].fillna(df_all['TEMP_PREFIX'].map(prefix_to_huyen))
    
    # Xã nếu hổng thì tạm điền là 'CHƯA RÕ' để Power BI không bị lỗi Null
    df_all['XA'] = df_all['XA'].fillna('CHƯA RÕ')
    
    # 2.3 Xử lý Tuổi và Giới tính Chủ hộ bị hổng
    # Lắp bằng giá trị trung vị (Median) và Yếu vị (Mode) của toàn Huyện đó
    df_all['TUOI_CHU_HO'] = df_all.groupby('HUYEN')['TUOI_CHU_HO'].transform(lambda x: x.fillna(x.median()))
    df_all['GIOI_TINH_CHU_HO'] = df_all.groupby('HUYEN')['GIOI_TINH_CHU_HO'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 1))
    
    # 2.4 Dân tộc: Nếu hổng thì lấy giá trị Dân tộc phổ biến nhất (Thường là 1 - Kinh)
    df_all['DANTOC_CHU_HO'] = df_all['DANTOC_CHU_HO'].fillna(1)

    # Dọn dẹp cột tạm
    df_all = df_all.drop(columns=['TEMP_PREFIX', 'SOURCE_FILE'], errors='ignore')

    print("3. ĐANG XUẤT FILE MASTER...")
    df_all.to_csv(output_filepath, index=False, encoding='utf-8-sig')
    print(f"-> THÀNH CÔNG! Đã lưu file chuẩn bị phân tích tại: {output_filepath}")
    print(f"-> Tổng số lượng hộ gia đình: {len(df_all):,} hộ.")
    print("-> SẴN SÀNG 100% CHO POWER BI VÀ MACHINE LEARNING!")

if __name__ == "__main__":
    # Đặt thư mục chứa 8 file HOUSEHOLD hiện tại của bạn
    input_folder = "Household_Data" 
    output_filepath = "DAK_NONG_HOUSEHOLDS_MASTER.csv"
    
    prepare_final_dataset(input_folder, output_filepath)