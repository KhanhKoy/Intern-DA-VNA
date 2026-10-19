import pandas as pd
import numpy as np
import re
import os

# =====================================================================
# TỪ ĐIỂN ÁNH XẠ DÂN TỘC (Dựa theo chuẩn Tổng cục Thống kê VN)
# =====================================================================
DANTOC_MAP = {
    'KINH': 1, 'TÀY': 2, 'THÁI': 3, 'HOA': 4, 'KHMER': 5, 'MƯỜNG': 6, 'NÙNG': 7, 'HMÔNG': 8, "H'MÔNG": 8, 'DAO': 9, 'GIA RAI': 10,
    'NGÁI': 11, 'Ê ĐÊ': 12, 'BA NA': 13, 'XƠ ĐĂNG': 14, 'SÁN CHAY': 15, 'CƠ HO': 16, 'CHĂM': 17, 'SÁN DÌU': 18, 'HRÊ': 19,
    'MNÔNG': 20, "M'NÔNG": 20, "M' NÔNG": 20, 'M NÔNG': 20, 'RA GLAI': 21, 'XTIÊNG': 22, 'BRU VÂN KIỀU': 23, 'THỔ': 24, 'GIÁY': 25,
    'CƠ TU': 26, 'GIẺ TRIÊNG': 27, 'MẠ': 28, 'KHƠ MÚ': 29, 'CO': 30, 'TÀ ÔI': 31, 'CHƠ RO': 32, 'KHÁNG': 33, 'XINH MUN': 34,
    'HÀ NHÌ': 35, 'CHU RU': 36, 'LÀO': 37, 'LA CHÍ': 38, 'LA HA': 39, 'PHÙ LÁ': 40, 'LA HỦ': 41, 'LỰ': 42, 'LÔ LÔ': 43,
    'CHỨT': 44, 'MẢNG': 45, 'PÀ THẺN': 46, 'CƠ LAO': 47, 'CỜ LAO': 47, 'CỐNG': 48, 'BỐ Y': 49, 'SI LA': 50, 'PU PÉO': 51, 'BRÂU': 52, 'Ơ ĐU': 53, 'RƠ MĂM': 54
}

def normalize_dantoc(val):
    if pd.isna(val): return np.nan
    val_str = str(val).strip().upper()
    # Nếu đã là số thì giữ nguyên
    if val_str.isdigit() or val_str.replace('.0', '').isdigit():
        return int(float(val_str))
    # Nếu là chữ, tìm trong từ điển
    for k, v in DANTOC_MAP.items():
        if k in val_str:
            return v
    return val # Trả về giá trị gốc nếu không khớp để xử lý nhiễu sau

# =====================================================================
# HÀM BỔ TRỢ: XỬ LÝ CCCD VÀ DINHDANH
# =====================================================================
def clean_cccd_strict_logic(row):
    cccd_raw = str(row['SO_CCCD']) if 'SO_CCCD' in row and pd.notna(row['SO_CCCD']) else ""
    dinhdanh_raw = str(row['DC_DINHDANH']) if 'DC_DINHDANH' in row and pd.notna(row['DC_DINHDANH']) else ""
    
    cccd_digits = re.sub(r'\D', '', cccd_raw)
    dinhdanh_digits = re.sub(r'\D', '', dinhdanh_raw)
    
    if len(cccd_digits) == 12: return cccd_digits
    if len(dinhdanh_digits) == 12: return dinhdanh_digits
    elif len(dinhdanh_digits) in [10, 11] and not dinhdanh_digits.startswith('0'):
        return dinhdanh_digits.zfill(12)
    
    if len(cccd_digits) in [10, 11]:
        if not cccd_digits.startswith('0'): return cccd_digits.zfill(12)
        else: return cccd_digits
    return cccd_digits if len(cccd_digits) > 0 else np.nan

# =====================================================================
# PIPELINE TIỀN XỬ LÝ VẠN NĂNG
# =====================================================================
def process_universal_dataset(input_filepath, output_filepath, ma_huyen_prefix):
    print(f"\n{'-'*60}")
    print(f"ĐANG TIỀN XỬ LÝ: {input_filepath}")
    print(f"{'-'*60}")
    
    xls = pd.ExcelFile(input_filepath)
    df = pd.read_excel(xls, sheet_name=0)
    if df.empty and len(xls.sheet_names) > 1:
        print("[!] Sheet 1 rỗng. Đã tự động chuyển sang đọc Sheet 2...")
        df = pd.read_excel(xls, sheet_name=1)

    # XỬ LÝ LỖI XUỐNG DÒNG (\n) TRONG TÊN CỘT CỦA CƯ JÚT
    df.columns = df.columns.str.replace('\n', '').str.replace(' ', '').str.upper()
    # Khôi phục đúng một số tên cột cho đồng nhất
    rename_dict = {'DANTOC': 'DANTOC', 'PHAN_LOAI_HO': 'PHAN_LOAI_HO', 'GIOI_TINH': 'GIOI_TINH'}
    df = df.rename(columns=rename_dict)
        
    cols_to_drop = [c for c in df.columns if 'UNNAMED' in str(c)]
    if cols_to_drop: df = df.drop(columns=cols_to_drop)
        
    df = df.astype(object)
    df['original_index'] = df.index

    # -------------------------------------------------------------
    # BƯỚC 1: XỬ LÝ LỖI VỠ CẤU TRÚC (ALIGNMENT SHIFTS)
    # -------------------------------------------------------------
    df_working = df.copy()
    
    # Lỗi Loại 3 (Đắk Mil): Dịch trái 2 ô bằng Column Shifting an toàn
    mask_left_shift = pd.Series([False]*len(df_working))
    if 'NGAY_SINH' in df_working.columns:
        mask_left_shift = df_working['NGAY_SINH'].astype(str).str.contains('ĐẮK|DAK', case=False, na=False)
        df_err_left = df_working[mask_left_shift].copy()
        if len(df_err_left) > 0:
            print(f"[+] Đã nắn {len(df_err_left)} dòng bị mất 2 cột đầu (Dịch trái)...")
            # Shift các giá trị sang phải 2 ô bằng cách dịch mảng numpy nhưng gắn vào object dataframe
            shifted_values = np.pad(df_err_left.iloc[:, :-1].values, ((0,0), (2,0)), mode='constant', constant_values=np.nan)[:, :-2]
            df_err_left.iloc[:, :-1] = shifted_values # Trừ cột original_index ở cuối
            df_working.loc[mask_left_shift] = df_err_left

    # Lỗi Loại 1 (Krông Nô): Mất TỈNH & HUYỆN
    mask_address = pd.Series([False]*len(df_working))
    if 'TINH' in df_working.columns:
        mask_address = (~mask_left_shift) & (df_working['TINH'].notna()) & (~df_working['TINH'].astype(str).str.contains('ĐẮK NÔNG|DAK NONG|DAKNONG|ĐĂK NÔNG', case=False))
        df_err_address = df_working[mask_address].copy()
        if len(df_err_address) > 0:
            print(f"[+] Đã nắn {len(df_err_address)} dòng bị mất cột Tỉnh/Huyện...")
            if 'KET_QUA' in df_err_address.columns and 'DANTOC' in df_err_address.columns: df_err_address['KET_QUA'] = df_err_address['DANTOC']
            if 'PHAN_LOAI_HO' in df_err_address.columns and 'XA' in df_err_address.columns: df_err_address['PHAN_LOAI_HO'] = df_err_address['XA']
            if 'DANTOC' in df_err_address.columns and 'HUYEN' in df_err_address.columns: df_err_address['DANTOC'] = df_err_address['HUYEN']
            if 'XA' in df_err_address.columns and 'TINH' in df_err_address.columns: df_err_address['XA'] = df_err_address['TINH']
            df_err_address['TINH'] = 'ĐẮK NÔNG'
            df_working.loc[mask_address] = df_err_address

    # Lỗi Loại 2: Ngày sinh trượt vào cột QUANHE_CHUHO
    mask_relation = pd.Series([False]*len(df_working))
    if 'QUANHE_CHUHO' in df_working.columns:
        mask_relation = df_working['QUANHE_CHUHO'].astype(str).str.contains(r'-|/|\b19\d{2}\b|\b20\d{2}\b', regex=True, na=False)
        mask_relation = mask_relation & (~mask_address) & (~mask_left_shift)
        df_err_relation = df_working[mask_relation].copy()
        if len(df_err_relation) > 0:
            print(f"[+] Đã nắn {len(df_err_relation)} dòng bị trượt Ngày sinh vào Quan hệ...")
            if 'NGAY_SINH' in df_err_relation.columns: df_err_relation['NGAY_SINH'] = df_err_relation['QUANHE_CHUHO']
            is_ch = (df_err_relation['HO_TEN_THANH_VIEN'].astype(str).str.strip().str.lower() == 
                     df_err_relation['HO_TEN_CHU_HO'].astype(str).str.strip().str.lower())
            df_err_relation['QUANHE_CHUHO'] = np.where(is_ch, 1, 3)
            df_working.loc[mask_relation] = df_err_relation

    df_final = df_working.sort_values('original_index').reset_index(drop=True)
    df_final = df_final.drop(columns=['original_index'])

    # -------------------------------------------------------------
    # BƯỚC 2: XỬ LÝ LỌC NHIỄU (NGƯỜI ĐÃ CHẾT) VÀ DÂN TỘC (CHỮ -> SỐ)
    # -------------------------------------------------------------
    if 'DANTOC' in df_final.columns:
        df_final['DANTOC'] = df_final['DANTOC'].apply(normalize_dantoc)

    cccd_raw = df_final['SO_CCCD'].astype(str).str.strip().str.lower() if 'SO_CCCD' in df_final.columns else pd.Series('')
    ghi_chu_raw = df_final['GHI_CHU'].astype(str).str.strip().str.lower() if 'GHI_CHU' in df_final.columns else pd.Series('')
    is_dead = cccd_raw.str.contains('chết|mất|qua đời|từ trần|đã chết', regex=True, na=False) | \
              ghi_chu_raw.str.contains('chết|mất|qua đời|từ trần|đã chết', regex=True, na=False)
    
    if is_dead.sum() > 0:
        print(f"[+] Đã loại bỏ {is_dead.sum()} nhân khẩu (Đã chết/Qua đời).")
        df_final = df_final[~is_dead].copy()
    
    # -------------------------------------------------------------
    # BƯỚC 3: ĐÁNH LẠI MÃ HỘ GIA ĐÌNH (GLOBAL ID)
    # -------------------------------------------------------------
    is_chu_ho = (df_final['QUANHE_CHUHO'].astype(str).str.strip().isin(['1', '1.0'])) | \
                (df_final['HO_TEN_CHU_HO'].astype(str).str.strip().str.lower() == df_final['HO_TEN_THANH_VIEN'].astype(str).str.strip().str.lower())
    
    df_final['STT_HO'] = is_chu_ho.cumsum()
    df_final['STT_HO'] = df_final['STT_HO'].replace(0, np.nan).ffill().fillna(1).astype(int)
    df_final['ID_HO_GLOBAL'] = ma_huyen_prefix + "_" + df_final['STT_HO'].astype(str)

    # -------------------------------------------------------------
    # BƯỚC 4: LÀM SẠCH CCCD CHUẨN ĐỂ CỨU DỮ LIỆU
    # -------------------------------------------------------------
    df_final['SO_CCCD_CLEAN'] = df_final.apply(clean_cccd_strict_logic, axis=1)
    df_final['HAS_VALID_CCCD'] = np.where(df_final['SO_CCCD_CLEAN'].astype(str).str.len() == 12, 1, 0)

    # -------------------------------------------------------------
    # BƯỚC 5: TRÍCH XUẤT NĂM SINH & TÍNH TUỔI (2023)
    # -------------------------------------------------------------
    years_from_ngaysinh = df_final['NGAY_SINH'].astype(str).str.extract(r'(\b(?:19|20)\d{2}\b)')[0] if 'NGAY_SINH' in df_final.columns else pd.Series(np.nan)
    
    def extract_year_from_cccd(cccd_str):
        if isinstance(cccd_str, str) and len(cccd_str) == 12:
            century_code, yy = cccd_str[3], int(cccd_str[4:6])
            if century_code in ['0', '1']: return 1900 + yy
            elif century_code in ['2', '3']: return 2000 + yy
        return np.nan

    years_from_cccd = df_final['SO_CCCD_CLEAN'].apply(extract_year_from_cccd)
    
    final_nam_sinh = pd.to_numeric(years_from_ngaysinh, errors='coerce').fillna(pd.to_numeric(years_from_cccd, errors='coerce'))
    df_final['NAM_SINH'] = final_nam_sinh
    df_final['TUOI'] = 2023 - df_final['NAM_SINH']
    
    # Dọn dẹp cột thô
    cols_to_drop_final = ['NGAY_SINH', 'SO_CCCD', 'DC_DINHDANH', 'DC_CMND', 'STT']
    df_final = df_final.drop(columns=[c for c in cols_to_drop_final if c in df_final.columns])

    # -------------------------------------------------------------
    # BƯỚC 6: XUẤT FILE SẠCH
    # -------------------------------------------------------------
    df_final.to_excel(output_filepath, index=False)
    print(f"-> Hoàn thành! Xuất file tại: {output_filepath} | Tổng số hộ: {df_final['ID_HO_GLOBAL'].nunique()}")

# ==========================================
# THỰC THI HÀNG LOẠT CHO 8 FILE
# ==========================================
if __name__ == "__main__":
    input_dir = r"Dữ liệu chuẩn hóa\CẬP NHẬT 20.9.2023" # Đổi lại đường dẫn phù hợp máy bạn
    output_dir = "Cleaned_Data"
    os.makedirs(output_dir, exist_ok=True)
    
    files_config = [
        {"filename": "HUYỆN KRÔNG NÔ.xlsx", "prefix": "KN"},
        {"filename": "HUYỆN DAK MIL.xlsx", "prefix": "DM"},
        {"filename": "HUYỆN CƯ JUT.xlsx", "prefix": "CJ"},
        {"filename": "Huyện Đắk Glong.xlsx", "prefix": "DGL"},
        {"filename": "HUYỆN ĐẮK RLẤP.xlsx", "prefix": "DRL"},
        {"filename": "HUYỆN ĐẮK SONG.xlsx", "prefix": "DS"},
        {"filename": "HUYỆN TUY ĐỨC.xlsx", "prefix": "TD"},
        {"filename": "TP GIA NGHĨA.xlsx", "prefix": "GN"}
    ]
    
    for config in files_config:
        in_path = os.path.join(input_dir, config["filename"])
        out_path = os.path.join(output_dir, config["filename"].replace(".xlsx", "_CLEANED.xlsx"))
        
        if os.path.exists(in_path):
            try:
                process_universal_dataset(in_path, out_path, config["prefix"])
            except Exception as e:
                print(f"[ERROR] Quá trình xử lý {config['filename']} gặp lỗi: {e}")
        else:
            print(f"[!] Bỏ qua: Không tìm thấy file {in_path}")