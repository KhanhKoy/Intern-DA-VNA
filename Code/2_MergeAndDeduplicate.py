import pandas as pd
import numpy as np
import os
import glob

def merge_and_deduplicate(input_folder, output_filepath):
    print(f"{'='*60}")
    print("PHASE 2: HỢP NHẤT VÀ LỌC TRÙNG LẶP TOÀN CỤC (ENTITY RESOLUTION)")
    print(f"{'='*60}")
    
    # 1. QUÉT VÀ GỘP 8 FILE LẠI VỚI NHAU
    all_files = glob.glob(os.path.join(input_folder, "*_CLEANED.xlsx"))
    if not all_files:
        print("[!] Không tìm thấy file _CLEANED.xlsx nào. Hãy kiểm tra lại đường dẫn.")
        return
        
    print(f"[+] Đã tìm thấy {len(all_files)} file. Đang tiến hành gộp (Concat)...")
    df_list = []
    for f in all_files:
        # Ép buộc Pandas phải đọc các cột định danh dưới dạng Chuỗi (String)
        df = pd.read_excel(f, dtype={'SO_CCCD_CLEAN': str, 'ID_HO_GLOBAL': str})
        df_list.append(df)
        
    df_all = pd.concat(df_list, ignore_index=True)
    
    # -------------------------------------------------------------
    # KHẮC PHỤC TRIỆT ĐỂ SỐ 0 BỊ MẤT SAU KHI GỘP DATA
    # -------------------------------------------------------------
    df_all['SO_CCCD_CLEAN'] = df_all['SO_CCCD_CLEAN'].replace(['nan', 'NaN', 'None'], np.nan)
    mask_notna = df_all['SO_CCCD_CLEAN'].notna()
    df_all.loc[mask_notna, 'SO_CCCD_CLEAN'] = df_all.loc[mask_notna, 'SO_CCCD_CLEAN'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(12)

    print(f"-> Tổng số nhân khẩu toàn tỉnh ban đầu: {len(df_all):,} người.")

    # 2. CHUẨN HÓA TEXT ĐỂ CHỐNG SAI CHÍNH TẢ (Trường hợp 4 & 6)
    print("\n[+] Đang chuẩn hóa tên (viết hoa, xóa khoảng trắng thừa)...")
    df_all['HO_TEN_NORM'] = df_all['HO_TEN_THANH_VIEN'].astype(str).str.strip().str.upper()
    df_all['HO_TEN_NORM'] = df_all['HO_TEN_NORM'].replace(r'\s+', ' ', regex=True)

    # 3. LỌC CCCD RÁC / MƯỢN CCCD (Trường hợp 1)
    name_count_per_cccd = df_all[df_all['SO_CCCD_CLEAN'].notna()].groupby('SO_CCCD_CLEAN')['HO_TEN_NORM'].nunique()
    trash_cccds = name_count_per_cccd[name_count_per_cccd > 2].index
    print(f"[+] Phát hiện {len(trash_cccds)} số CCCD rác (1 số gán cho > 2 người). Đang Null hóa...")
    df_all.loc[df_all['SO_CCCD_CLEAN'].isin(trash_cccds), 'SO_CCCD_CLEAN'] = np.nan

    # 4. LỌC TRÙNG LẶP ĐỊNH DANH (Trường hợp 2, 3, 5)
    df_has_cccd = df_all[df_all['SO_CCCD_CLEAN'].notna()].copy()
    df_no_cccd = df_all[df_all['SO_CCCD_CLEAN'].isna()].copy()

    print("[+] Đang xếp hạng ưu tiên bản ghi (Single Source of Truth)...")
    # Xếp hạng: Chủ hộ (1) lên đầu. Trạng thái hộ nghèo (1) > Cận nghèo (2) > Bình thường (NaN)
    df_has_cccd = df_has_cccd.sort_values(
        by=['QUANHE_CHUHO', 'PHAN_LOAI_HO'], 
        ascending=[True, True], 
        na_position='last'
    )

    duplicates_count = df_has_cccd.duplicated(subset=['SO_CCCD_CLEAN'], keep='first').sum()
    print(f"[+] Đã hợp nhất và XÓA {duplicates_count:,} bản ghi nhân khẩu cũ do tách khẩu/thoát nghèo.")
    df_has_cccd_dedup = df_has_cccd.drop_duplicates(subset=['SO_CCCD_CLEAN'], keep='first')

    # 5. GỘP LẠI DỮ LIỆU CUỐI CÙNG
    df_final = pd.concat([df_has_cccd_dedup, df_no_cccd], ignore_index=True)
    df_final = df_final.drop(columns=['HO_TEN_NORM']) # Xóa cột phụ
    
    # -------------------------------------------------------------
    # 6. GOM NHÓM THÀNH VIÊN VỀ CÙNG MỘT HỘ GIA ĐÌNH (SẮP XẾP THEO SỐ THỨ TỰ TỰ NHIÊN)
    # -------------------------------------------------------------
    print("[+] Đang sắp xếp các thành viên về chung một hộ theo đúng số thứ tự (1, 2, 3...)...")
    
    # Tách phần chữ (tiền tố huyện, VD: 'CJ_') và phần số (STT hộ, VD: 1, 10, 100) để sắp xếp chuẩn toán học
    df_final['TEMP_PREFIX'] = df_final['ID_HO_GLOBAL'].str.extract(r'([A-Za-z_]+)')[0]
    df_final['TEMP_HID'] = pd.to_numeric(df_final['ID_HO_GLOBAL'].str.extract(r'(\d+)')[0], errors='coerce')
    
    # Sắp xếp theo: Tiền tố huyện -> Số thứ tự hộ (tăng dần tự nhiên) -> Quan hệ chủ hộ (Chủ hộ = 1 lên đầu)
    df_final = df_final.sort_values(
        by=['TEMP_PREFIX', 'TEMP_HID', 'QUANHE_CHUHO'],
        ascending=[True, True, True],
        na_position='last'
    )
    
    # Xóa các cột tạm dùng để sort
    df_final = df_final.drop(columns=['TEMP_PREFIX', 'TEMP_HID'])
    
    print(f"\n{'='*60}")
    print(f"-> HOÀN TẤT! Tổng số nhân khẩu thực tế toàn tỉnh: {len(df_final):,} người.")
    
    # -------------------------------------------------------------
    # 7. LƯU FILE CSV BẢO TOÀN SỐ 0
    # -------------------------------------------------------------
    mask_cccd = df_final['SO_CCCD_CLEAN'].notna()
    df_final.loc[mask_cccd, 'SO_CCCD_CLEAN'] = '\t' + df_final.loc[mask_cccd, 'SO_CCCD_CLEAN'].astype(str)
    
    df_final.to_csv(output_filepath, index=False, encoding='utf-8-sig')
    print(f"-> Đã lưu Master Data (CSV) tại: {output_filepath}")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Trỏ vào thư mục chứa các file _CLEANED.xlsx chuẩn cấu trúc mới
    input_folder = "Cleaned_Data_Master" 
    
    # Tên file tổng toàn tỉnh xuất ra
    output_filepath = "DAK_NONG_MASTER_POPULATION.csv" 
    
    merge_and_deduplicate(input_folder, output_filepath)