import pandas as pd
import numpy as np
import re
import os

DANTOC_MAP = {
    'KINH': 1, 'TÀY': 2, 'THÁI': 3, 'HOA': 4, 'KHMER': 5, 'MƯỜNG': 6, 'NÙNG': 7, 'HMÔNG': 8, "H'MÔNG": 8, 'DAO': 9, 'GIA RAI': 10,
    'NGÁI': 11, 'Ê ĐÊ': 12, 'BA NA': 13, 'XƠ ĐĂNG': 14, 'SÁN CHAY': 15, 'CƠ HO': 16, 'CHĂM': 17, 'SÁN DÌU': 18, 'HRÊ': 19,
    'MNÔNG': 20, "M'NÔNG": 20, "M' NÔNG": 20, 'M NÔNG': 20, 'RA GLAI': 21, 'XTIÊNG': 22, 'BRU VÂN KIỀU': 23, 'THỔ': 24, 'GIÁY': 25,
    'CƠ TU': 26, 'GIẺ TRIÊNG': 27, 'MẠ': 28, 'KHƠ MÚ': 29, 'CO': 30, 'TÀ ÔI': 31, 'CHƠ RO': 32, 'KHÁNG': 33, 'XINH MUN': 34
}

def normalize_dantoc(val):
    if pd.isna(val): return np.nan
    val_str = str(val).strip().upper()
    if val_str.isdigit() or val_str.replace('.0', '').isdigit(): return int(float(val_str))
    for k, v in DANTOC_MAP.items():
        if k in val_str: return v
    return val 

def clean_cccd_strict_logic(row):
    cccd_raw = str(row['SO_CCCD']) if 'SO_CCCD' in row and pd.notna(row['SO_CCCD']) else ""
    dinhdanh_raw = str(row['DC_DINHDANH']) if 'DC_DINHDANH' in row and pd.notna(row['DC_DINHDANH']) else ""
    cccd_digits = re.sub(r'\D', '', cccd_raw)
    dinhdanh_digits = re.sub(r'\D', '', dinhdanh_raw)
    
    if len(cccd_digits) == 12: return cccd_digits
    if len(dinhdanh_digits) == 12: return dinhdanh_digits
    elif len(dinhdanh_digits) in [10, 11] and not dinhdanh_digits.startswith('0'): return dinhdanh_digits.zfill(12)
    if len(cccd_digits) in [10, 11]:
        if not cccd_digits.startswith('0'): return cccd_digits.zfill(12)
        else: return cccd_digits
    return cccd_digits if len(cccd_digits) > 0 else np.nan

def process_krongno_only(input_filepath, output_filepath):
    print(f"{'='*60}")
    print(f"ĐANG CHỮA BỆNH CHO FILE KRÔNG NÔ")
    print(f"{'='*60}")
    
    xls = pd.ExcelFile(input_filepath)
    df = pd.read_excel(xls, sheet_name=0)
    if df.empty and len(xls.sheet_names) > 1: df = pd.read_excel(xls, sheet_name=1)

    df.columns = df.columns.str.replace('\n', '').str.replace(' ', '').str.upper()
    df = df.rename(columns={'DANTOC': 'DANTOC', 'PHAN_LOAI_HO': 'PHAN_LOAI_HO', 'GIOI_TINH': 'GIOI_TINH'})
    
    cols_to_drop = [c for c in df.columns if 'UNNAMED' in str(c)]
    if cols_to_drop: df = df.drop(columns=cols_to_drop)
    df = df.astype(object)
    df_working = df.copy()

    # -------------------------------------------------------------
    # 1. FIX LỖI MẤT TỈNH, HUYỆN (Dòng 11009-11360 và 2000+)
    # -------------------------------------------------------------
    mask_address = (df_working['TINH'].notna()) & (~df_working['TINH'].astype(str).str.contains('ĐẮK NÔNG|DAK NONG', case=False)) & (~df_working['TINH'].astype(str).str.match(r'^\d+$'))
    df_err_address = df_working[mask_address].copy()
    
    if len(df_err_address) > 0:
        print(f"[+] Tìm thấy {len(df_err_address)} dòng bị trượt Xã vào Tỉnh. Đang nắn lại...")
        # Đẩy dữ liệu sang phải về đúng vị trí
        if 'KET_QUA' in df_err_address.columns and 'DANTOC' in df_err_address.columns: df_err_address['KET_QUA'] = df_err_address['DANTOC']
        if 'PHAN_LOAI_HO' in df_err_address.columns and 'XA' in df_err_address.columns: df_err_address['PHAN_LOAI_HO'] = df_err_address['XA']
        if 'DANTOC' in df_err_address.columns and 'HUYEN' in df_err_address.columns: df_err_address['DANTOC'] = df_err_address['HUYEN']
        if 'XA' in df_err_address.columns and 'TINH' in df_err_address.columns: df_err_address['XA'] = df_err_address['TINH']
        
        # BỔ SUNG QUAN TRỌNG: Gắn cứng lại Tỉnh và Huyện
        df_err_address['TINH'] = 'ĐẮK NÔNG'
        df_err_address['HUYEN'] = 'KRÔNG NÔ'
        df_working.loc[mask_address] = df_err_address

    # -------------------------------------------------------------
    # 2. FIX LỖI NGÀY SINH TRƯỢT VÀO QUAN HỆ CHỦ HỘ
    # -------------------------------------------------------------
    if 'QUANHE_CHUHO' in df_working.columns:
        mask_relation = df_working['QUANHE_CHUHO'].astype(str).str.contains(r'-|/|\b19\d{2}\b|\b20\d{2}\b', regex=True, na=False)
        df_err_relation = df_working[mask_relation].copy()
        if len(df_err_relation) > 0:
            print(f"[+] Tìm thấy {len(df_err_relation)} dòng bị trượt Ngày sinh vào Quan hệ Chủ hộ. Đang nắn lại...")
            if 'NGAY_SINH' in df_err_relation.columns: df_err_relation['NGAY_SINH'] = df_err_relation['QUANHE_CHUHO']
            
            # Khôi phục Quan hệ chủ hộ dựa trên đối chiếu Tên
            is_ch = (df_err_relation['HO_TEN_THANH_VIEN'].astype(str).str.strip().str.lower() == 
                     df_err_relation['HO_TEN_CHU_HO'].astype(str).str.strip().str.lower())
            df_err_relation['QUANHE_CHUHO'] = np.where(is_ch, 1, 3)
            df_working.loc[mask_relation] = df_err_relation

    df_final = df_working.copy()

    # -------------------------------------------------------------
    # 3. LÀM SẠCH, ĐÁNH MÃ VÀ TRÍCH XUẤT NGÀY THÁNG NĂM
    # -------------------------------------------------------------
    print("[+] Đang loại bỏ người chết và đánh mã hộ (ID_HO_GLOBAL)...")
    if 'DANTOC' in df_final.columns: df_final['DANTOC'] = df_final['DANTOC'].apply(normalize_dantoc)

    cccd_raw = df_final['SO_CCCD'].astype(str).str.strip().str.lower() if 'SO_CCCD' in df_final.columns else pd.Series('')
    ghi_chu_raw = df_final['GHI_CHU'].astype(str).str.strip().str.lower() if 'GHI_CHU' in df_final.columns else pd.Series('')
    is_dead = cccd_raw.str.contains('chết|mất|qua đời|từ trần|đã chết', regex=True, na=False) | ghi_chu_raw.str.contains('chết|mất|qua đời|từ trần|đã chết', regex=True, na=False)
    if is_dead.sum() > 0: df_final = df_final[~is_dead].copy()
    
    is_chu_ho = (df_final['QUANHE_CHUHO'].astype(str).str.strip().isin(['1', '1.0'])) | \
                (df_final['HO_TEN_CHU_HO'].astype(str).str.strip().str.lower() == df_final['HO_TEN_THANH_VIEN'].astype(str).str.strip().str.lower())
    df_final['STT_HO'] = is_chu_ho.cumsum()
    df_final['STT_HO'] = df_final['STT_HO'].replace(0, np.nan).ffill().fillna(1).astype(int)
    df_final['ID_HO_GLOBAL'] = "KN_" + df_final['STT_HO'].astype(str)

    df_final['SO_CCCD_CLEAN'] = df_final.apply(clean_cccd_strict_logic, axis=1)
    df_final['HAS_VALID_CCCD'] = np.where(df_final['SO_CCCD_CLEAN'].astype(str).str.len() == 12, 1, 0)
    
    # Ép lỗi Excel Date về Date thường
    def fix_excel_date(val):
        val_str = str(val).strip()
        if val_str.isdigit() and 10000 < int(val_str) < 50000:
            return (pd.to_datetime('1899-12-30') + pd.to_timedelta(int(val_str), 'D')).strftime('%d/%m/%Y')
        return val
    df_final['NGAY_SINH'] = df_final['NGAY_SINH'].apply(fix_excel_date)

    # Bóc tách
    years_from_ns = df_final['NGAY_SINH'].astype(str).str.extract(r'(\b(?:19|20)\d{2}\b)')[0]
    months_from_ns = df_final['NGAY_SINH'].astype(str).str.extract(r'(?:/|-)(\d{1,2})(?:/|-)(?:19|20)\d{2}')[0]
    days_from_ns = df_final['NGAY_SINH'].astype(str).str.extract(r'^(\d{1,2})(?:/|-)')[0]
    
    df_final['NGAY'] = pd.to_numeric(days_from_ns, errors='coerce').astype('Int64')
    df_final['THANG'] = pd.to_numeric(months_from_ns, errors='coerce').astype('Int64')
    
    def extract_year_from_cccd(cccd_str):
        if isinstance(cccd_str, str) and len(cccd_str) == 12:
            century_code, yy = cccd_str[3], int(cccd_str[4:6])
            if century_code in ['0', '1']: return 1900 + yy
            elif century_code in ['2', '3']: return 2000 + yy
        return np.nan
    years_from_cccd = df_final['SO_CCCD_CLEAN'].apply(extract_year_from_cccd)
    
    df_final['NAM_SINH'] = pd.to_numeric(years_from_ns, errors='coerce').fillna(pd.to_numeric(years_from_cccd, errors='coerce')).astype('Int64')
    df_final['TUOI'] = 2023 - df_final['NAM_SINH']
    
    # -------------------------------------------------------------
    # 4. CHỈNH LẠI CẤU TRÚC VÀ XUẤT FILE
    # -------------------------------------------------------------
    cols_to_drop_final = ['NGAY_SINH', 'SO_CCCD', 'DC_DINHDANH', 'DC_CMND', 'STT']
    df_final = df_final.drop(columns=[c for c in cols_to_drop_final if c in df_final.columns])

    order = ['ID_HO_GLOBAL', 'HO_TEN_CHU_HO', 'HO_TEN_THANH_VIEN', 'QUANHE_CHUHO', 'GIOI_TINH', 
             'NGAY', 'THANG', 'NAM_SINH', 'TUOI', 'TINH', 'HUYEN', 'XA', 'DANTOC', 
             'PHAN_LOAI_HO', 'KET_QUA', 'GHI_CHU', 'SO_CCCD_CLEAN', 'HAS_VALID_CCCD']
    
    for col in order:
        if col not in df_final.columns: df_final[col] = np.nan
    df_final = df_final[order]

    df_final.to_excel(output_filepath, index=False)
    print(f"-> HOÀN TẤT! Đã xuất Krông Nô SẠCH CHUẨN tại: {output_filepath}")

if __name__ == "__main__":
    # Thay đổi đường dẫn đến file Krông Nô chưa được làm sạch
    input_file = r"Dữ liệu chuẩn hóa\CẬP NHẬT 20.9.2023\HUYỆN KRÔNG NÔ.xlsx" 
    
    output_dir = "Cleaned_Data_Master"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "HUYỆN KRÔNG NÔ_CLEANED.xlsx")
    
    process_krongno_only(input_file, output_file)