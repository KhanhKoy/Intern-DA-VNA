import pandas as pd
import numpy as np
import re
import os

# =====================================================================
# TỪ ĐIỂN ÁNH XẠ DÂN TỘC 
# =====================================================================
DANTOC_MAP = {
    'KINH': 1, 'TÀY': 2, 'THÁI': 3, 'HOA': 4, 'KHMER': 5, 'MƯỜNG': 6, 'NÙNG': 7, 'HMÔNG': 8, "H'MÔNG": 8, 'DAO': 9, 'GIA RAI': 10,
    'NGÁI': 11, 'Ê ĐÊ': 12, 'BA NA': 13, 'XƠ ĐĂNG': 14, 'SÁN CHAY': 15, 'CƠ HO': 16, 'CHĂM': 17, 'SÁN DÌU': 18, 'HRÊ': 19,
    'MNÔNG': 20, "M'NÔNG": 20, "M' NÔNG": 20, 'M NÔNG': 20, 'RA GLAI': 21, 'XTIÊNG': 22, 'BRU VÂN KIỀU': 23, 'THỔ': 24, 'GIÁY': 25,
    'CƠ TU': 26, 'GIẺ TRIÊNG': 27, 'MẠ': 28, 'KHƠ MÚ': 29, 'CO': 30, 'TÀ ÔI': 31, 'CHƠ RO': 32, 'KHÁNG': 33, 'XINH MUN': 34
}

def normalize_dantoc(val):
    if pd.isna(val): return np.nan
    val_str = str(val).strip().upper()
    if val_str.isdigit() or val_str.replace('.0', '').isdigit():
        return int(float(val_str))
    for k, v in DANTOC_MAP.items():
        if k in val_str:
            return v
    return val 

# =====================================================================
# THUẬT TOÁN AI GIẢI CỨU TỪNG DÒNG BỊ VỠ NÁT CỦA ĐẮK MIL
# =====================================================================
def ai_rescue_broken_row(row):
    vals = [str(x).strip() for x in row.values if pd.notna(x)]
    ngay_sinh, cccd, xa, gioi_tinh = np.nan, np.nan, np.nan, np.nan
    names = []

    # 1. BẮT XÃ (ĐẮK SẮK, ĐẮK N'DRÓT, ĐẮK R'LA...)
    for v in vals:
        if 'ĐẮK' in v.upper() or 'DAK' in v.upper() or 'ĐĂK' in v.upper():
            if v.upper() not in ['ĐẮK NÔNG', 'DAK NONG', 'ĐĂK NÔNG', 'ĐĂK MIL', 'ĐẮK MIL']:
                xa = v
                break

    # 2. BẮT NGÀY SINH
    for v in vals:
        if re.search(r'\b(?:19|20)\d{2}\b', v) and ('/' in v or '-' in v):
            ngay_sinh = v.replace('//', '/') 
            break
        if v.isdigit() and 10000 < int(v) < 50000:
            ngay_sinh = (pd.to_datetime('1899-12-30') + pd.to_timedelta(int(v), 'D')).strftime('%d/%m/%Y')
            break
            
    # 3. BẮT CCCD 
    for v in vals:
        v_clean = v.replace('.0', '').replace("'", "")
        if len(v_clean) in [8, 9, 10, 11, 12] and v_clean.isdigit():
            if str(ngay_sinh) not in v and not re.search(r'\b(?:19|20)\d{2}\b', v) or (len(v_clean) >= 9):
                cccd = v_clean
                break
        if 'E+10' in v.upper() or 'E+09' in v.upper():
            try: cccd = str(int(float(v))) ; break
            except: pass

    # 4. BẮT TÊN 
    for v in vals:
        v_upper = v.upper()
        if len(v) > 4 and not any(c.isdigit() for c in v):
            if all(x not in v_upper for x in ['ĐẮK', 'DAK', 'TIM THAY', 'KHONG', 'KINH', 'M NÔNG', 'DAO', 'TÀY']):
                names.append(v)
                
    ten_ch, ten_tv = np.nan, np.nan
    if len(names) >= 2:
        ten_ch, ten_tv = names[0], names[1]
    elif len(names) == 1:
        ten_ch = ten_tv = names[0]

    # 5. BẮT GIỚI TÍNH
    for v in vals:
        if v in ['1', '2', '1.0', '2.0']:
            gioi_tinh = str(int(float(v)))
            break

    # 6. GẮN LẠI DÒNG
    new_row = pd.Series(index=row.index, dtype=object)
    if pd.notna(ten_ch): new_row['HO_TEN_CHU_HO'] = ten_ch
    if pd.notna(ten_tv): new_row['HO_TEN_THANH_VIEN'] = ten_tv
    if pd.notna(ngay_sinh): new_row['NGAY_SINH'] = ngay_sinh
    if pd.notna(cccd): new_row['SO_CCCD'] = cccd
    if pd.notna(xa): new_row['XA'] = xa
    if pd.notna(gioi_tinh): new_row['GIOI_TINH'] = gioi_tinh
    
    if pd.notna(ten_ch) and pd.notna(ten_tv):
        new_row['QUANHE_CHUHO'] = '1' if ten_ch.strip() == ten_tv.strip() else '3'
        
    new_row['TINH'] = 'ĐẮK NÔNG'
    return new_row

# =====================================================================
# PIPELINE TIỀN XỬ LÝ VẠN NĂNG (GỘP ĐẮK MIL & KRÔNG NÔ & CHUNG)
# =====================================================================
def process_universal_dataset(input_filepath, output_filepath, ma_huyen_prefix):
    print(f"\n{'-'*60}")
    print(f"ĐANG TIỀN XỬ LÝ: {os.path.basename(input_filepath)}")
    
    xls = pd.ExcelFile(input_filepath)
    df = pd.read_excel(xls, sheet_name=0)
    if df.empty and len(xls.sheet_names) > 1: df = pd.read_excel(xls, sheet_name=1)
    
    # 1. CHUẨN HÓA TÊN CỘT
    df.columns = df.columns.str.replace('\n', '').str.replace(' ', '').str.upper()
    rename_dict = {'DANTOC': 'DANTOC', 'PHAN_LOAI_HO': 'PHAN_LOAI_HO', 'GIOI_TINH': 'GIOI_TINH'}
    df = df.rename(columns=rename_dict)
    cols_to_drop = [c for c in df.columns if 'UNNAMED' in str(c)]
    if cols_to_drop: df = df.drop(columns=cols_to_drop)
    df = df.astype(object)
    df_working = df.copy()

    # -------------------------------------------------------------
    # BƯỚC 1: XỬ LÝ LỖI VỠ CẤU TRÚC 
    # -------------------------------------------------------------
    # TRƯỜNG HỢP 1: Dòng nát của Đắk Mil (Tỉnh bị mất hoặc chạy linh tinh)
    mask_ai_error = (~df_working['TINH'].astype(str).str.contains('ĐẮK NÔNG|DAK NONG|ĐĂK NÔNG', case=False, na=False)) & \
                    (df_working['TINH'].astype(str).str.contains('ĐẮK SẮK|ĐẮK MIL|N\'DRÓT|ĐỨC MINH', case=False, na=False) | df_working['TINH'].isna())
    
    if mask_ai_error.sum() > 0:
        print(f"[+] Dùng AI dọn rác {mask_ai_error.sum()} dòng vỡ cấu trúc nặng...")
        df_working.loc[mask_ai_error] = df_working.loc[mask_ai_error].apply(ai_rescue_broken_row, axis=1)

    # TRƯỜNG HỢP 2: Lỗi dịch cột phần đuôi của Krông Nô (Xã chạy vào Tỉnh)
    mask_address = (df_working['TINH'].notna()) & (~df_working['TINH'].astype(str).str.contains('ĐẮK NÔNG|DAK NONG|DAKNONG|ĐĂK NÔNG|DAKNONG', case=False)) & (~df_working['TINH'].astype(str).str.match(r'^\d+$'))
    df_err_address = df_working[mask_address].copy()
    if len(df_err_address) > 0:
        print(f"[+] Nắn {len(df_err_address)} dòng bị trượt Xã vào Tỉnh (Lỗi Krông Nô)...")
        if 'KET_QUA' in df_err_address.columns and 'DANTOC' in df_err_address.columns: df_err_address['KET_QUA'] = df_err_address['DANTOC']
        if 'PHAN_LOAI_HO' in df_err_address.columns and 'XA' in df_err_address.columns: df_err_address['PHAN_LOAI_HO'] = df_err_address['XA']
        if 'DANTOC' in df_err_address.columns and 'HUYEN' in df_err_address.columns: df_err_address['DANTOC'] = df_err_address['HUYEN']
        if 'XA' in df_err_address.columns and 'TINH' in df_err_address.columns: df_err_address['XA'] = df_err_address['TINH']
        df_err_address['TINH'] = 'ĐẮK NÔNG'
        df_working.loc[mask_address] = df_err_address

    # TRƯỜNG HỢP 3: Ngày sinh trượt vào cột QUANHE_CHUHO (Lỗi Krông Nô)
    if 'QUANHE_CHUHO' in df_working.columns:
        mask_relation = df_working['QUANHE_CHUHO'].astype(str).str.contains(r'-|/|\b19\d{2}\b|\b20\d{2}\b', regex=True, na=False)
        df_err_relation = df_working[mask_relation].copy()
        if len(df_err_relation) > 0:
            print(f"[+] Nắn {len(df_err_relation)} dòng bị trượt Ngày sinh vào Quan hệ...")
            if 'NGAY_SINH' in df_err_relation.columns: df_err_relation['NGAY_SINH'] = df_err_relation['QUANHE_CHUHO']
            is_ch = (df_err_relation['HO_TEN_THANH_VIEN'].astype(str).str.strip().str.lower() == 
                     df_err_relation['HO_TEN_CHU_HO'].astype(str).str.strip().str.lower())
            df_err_relation['QUANHE_CHUHO'] = np.where(is_ch, 1, 3)
            df_working.loc[mask_relation] = df_err_relation

    df_final = df_working.copy()

    # -------------------------------------------------------------
    # BƯỚC 2: XỬ LÝ LỌC NHIỄU NGƯỜI ĐÃ CHẾT & CHUẨN HÓA DÂN TỘC
    # -------------------------------------------------------------
    if 'DANTOC' in df_final.columns: df_final['DANTOC'] = df_final['DANTOC'].apply(normalize_dantoc)

    cccd_raw = df_final['SO_CCCD'].astype(str).str.strip().str.lower() if 'SO_CCCD' in df_final.columns else pd.Series('')
    ghi_chu_raw = df_final['GHI_CHU'].astype(str).str.strip().str.lower() if 'GHI_CHU' in df_final.columns else pd.Series('')
    is_dead = cccd_raw.str.contains('chết|mất|qua đời|từ trần|đã chết', regex=True, na=False) | ghi_chu_raw.str.contains('chết|mất|qua đời|từ trần|đã chết', regex=True, na=False)
    
    if is_dead.sum() > 0: df_final = df_final[~is_dead].copy()

    # -------------------------------------------------------------
    # BƯỚC 3: ĐÁNH MÃ ID HỘ
    # -------------------------------------------------------------
    is_chu_ho = (df_final['QUANHE_CHUHO'].astype(str).str.strip().isin(['1', '1.0'])) | \
                (df_final['HO_TEN_CHU_HO'].astype(str).str.strip().str.lower() == df_final['HO_TEN_THANH_VIEN'].astype(str).str.strip().str.lower())
    df_final['STT_HO'] = is_chu_ho.cumsum()
    df_final['STT_HO'] = df_final['STT_HO'].replace(0, np.nan).ffill().fillna(1).astype(int)
    df_final['ID_HO_GLOBAL'] = ma_huyen_prefix + "_" + df_final['STT_HO'].astype(str)

    # -------------------------------------------------------------
    # BƯỚC 4: LÀM SẠCH CCCD
    # -------------------------------------------------------------
    def clean_cccd(val):
        v = re.sub(r'\D', '', str(val))
        if len(v) in [10, 11] and not v.startswith('0'): return v.zfill(12)
        if len(v) == 12: return v
        return np.nan

    df_final['SO_CCCD_CLEAN'] = df_final['SO_CCCD'].apply(clean_cccd) if 'SO_CCCD' in df_final.columns else np.nan
    df_final['HAS_VALID_CCCD'] = np.where(df_final['SO_CCCD_CLEAN'].notna(), 1, 0)

    # -------------------------------------------------------------
    # BƯỚC 5: TRÍCH XUẤT NGÀY, THÁNG, NĂM SINH CHUẨN
    # -------------------------------------------------------------
    if 'NGAY_SINH' in df_final.columns:
        # Bóc Năm
        years_from_ns = df_final['NGAY_SINH'].astype(str).str.extract(r'(\b(?:19|20)\d{2}\b)')[0]
        # Bóc Tháng
        months_from_ns = df_final['NGAY_SINH'].astype(str).str.extract(r'(?:/|-)(\d{1,2})(?:/|-)(?:19|20)\d{2}')[0]
        # Bóc Ngày
        days_from_ns = df_final['NGAY_SINH'].astype(str).str.extract(r'^(\d{1,2})(?:/|-)')[0]
        
        df_final['NGAY'] = pd.to_numeric(days_from_ns, errors='coerce').astype('Int64')
        df_final['THANG'] = pd.to_numeric(months_from_ns, errors='coerce').astype('Int64')
        
        # Bổ sung năm từ CCCD nếu không có
        def get_year_from_cccd(cccd_str):
            if isinstance(cccd_str, str) and len(cccd_str) == 12:
                century_code, yy = cccd_str[3], int(cccd_str[4:6])
                if century_code in ['0', '1']: return 1900 + yy
                elif century_code in ['2', '3']: return 2000 + yy
            return np.nan
        years_from_cccd = df_final['SO_CCCD_CLEAN'].apply(get_year_from_cccd)
        
        df_final['NAM_SINH'] = pd.to_numeric(years_from_ns, errors='coerce').fillna(pd.to_numeric(years_from_cccd, errors='coerce')).astype('Int64')
        df_final['TUOI'] = 2023 - df_final['NAM_SINH']
    
    # -------------------------------------------------------------
    # BƯỚC 6: CHỈNH LẠI CẤU TRÚC VÀ XUẤT FILE ĐỒNG NHẤT
    # -------------------------------------------------------------
    # Sắp xếp đúng theo trật tự đẹp mắt để tiện concat
    order = ['ID_HO_GLOBAL', 'HO_TEN_CHU_HO', 'HO_TEN_THANH_VIEN', 'QUANHE_CHUHO', 'GIOI_TINH', 
             'NGAY', 'THANG', 'NAM_SINH', 'TUOI', 'TINH', 'HUYEN', 'XA', 'DANTOC', 
             'PHAN_LOAI_HO', 'KET_QUA', 'GHI_CHU', 'SO_CCCD_CLEAN', 'HAS_VALID_CCCD']
    
    df_final = df_final[[c for c in order if c in df_final.columns]]

    df_final.to_excel(output_filepath, index=False)
    print(f"-> Hoàn thành! Xuất file tại: {output_filepath}")

if __name__ == "__main__":
    input_dir = r"Dữ liệu chuẩn hóa\CẬP NHẬT 20.9.2023" # Đổi lại đường dẫn phù hợp máy bạn
    output_dir = "Cleaned_Data_Master"
    os.makedirs(output_dir, exist_ok=True)
    
    files_config = [
        # {"filename": "HUYỆN KRÔNG NÔ.xlsx", "prefix": "KN"},
        # {"filename": "HUYỆN DAK MIL.xlsx", "prefix": "DM"},
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