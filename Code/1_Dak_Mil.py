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

# =================================================================================
# THUẬT TOÁN AI GIẢI CỨU TỪNG DÒNG BỊ VỠ NÁT CỦA ĐẮK MIL
# Bất chấp người nhập liệu xóa bao nhiêu ô, thuật toán sẽ tự động gắp đúng vào cột
# =================================================================================
def ai_rescue_broken_row(row):
    # Lấy toàn bộ giá trị đang có trên dòng này
    vals = [str(x).strip() for x in row.values if pd.notna(x)]
    
    ngay_sinh, cccd, xa, gioi_tinh = np.nan, np.nan, np.nan, np.nan
    names = []

    # 1. BẮT XÃ (ĐẮK SẮK, ĐẮK N'DRÓT, ĐẮK R'LA...)
    for v in vals:
        if 'ĐẮK' in v.upper() or 'DAK' in v.upper() or 'ĐĂK' in v.upper():
            if v.upper() not in ['ĐẮK NÔNG', 'DAK NONG', 'ĐĂK NÔNG', 'ĐĂK MIL', 'ĐẮK MIL']:
                xa = v
                break

    # 2. BẮT NGÀY SINH (Chứa 19xx/20xx và có dấu / hoặc -, hoặc số Serial của Excel)
    for v in vals:
        # Bắt ngày tháng có chứa dấu / hoặc -
        if re.search(r'\b(?:19|20)\d{2}\b', v) and ('/' in v or '-' in v):
            ngay_sinh = v.replace('//', '/') # Fix lỗi gõ 2 dấu // (Ví dụ: 2//10/1966)
            break
        # Bắt lỗi Excel Date (Số nguyên từ 10000 -> 50000. VD: 13150 = 30/01/1936)
        if v.isdigit() and 10000 < int(v) < 50000:
            ngay_sinh = (pd.to_datetime('1899-12-30') + pd.to_timedelta(int(v), 'D')).strftime('%d/%m/%Y')
            break
            
    # 3. BẮT CCCD (Đủ 8 -> 12 chữ số)
    for v in vals:
        v_clean = v.replace('.0', '').replace("'", "")
        if len(v_clean) in [8, 9, 10, 11, 12] and v_clean.isdigit():
            # Tránh nhận nhầm Xã hoặc Ngày sinh
            if str(ngay_sinh) not in v and not re.search(r'\b(?:19|20)\d{2}\b', v) or (len(v_clean) >= 9):
                cccd = v_clean
                break
        # Nếu bị Excel ép kiểu khoa học (VD: 6.71E+10)
        if 'E+10' in v.upper() or 'E+09' in v.upper():
            try: cccd = str(int(float(v))) ; break
            except: pass

    # 4. BẮT TÊN CHỦ HỘ & THÀNH VIÊN
    for v in vals:
        v_upper = v.upper()
        # Tên phải dài hơn 4 ký tự, không chứa số, không phải là Tỉnh/Huyện/Xã/Kết quả
        if len(v) > 4 and not any(c.isdigit() for c in v):
            if all(x not in v_upper for x in ['ĐẮK', 'DAK', 'TIM THAY', 'KHONG', 'KINH', 'M NÔNG', 'DAO', 'TÀY']):
                names.append(v)
                
    ten_ch, ten_tv = np.nan, np.nan
    if len(names) >= 2:
        ten_ch, ten_tv = names[0], names[1]
    elif len(names) == 1:
        ten_ch = ten_tv = names[0]

    # 5. BẮT GIỚI TÍNH (1 hoặc 2)
    # Lọc bỏ các số linh tinh, chỉ bắt số 1 hoặc 2 đứng một mình
    for v in vals:
        if v in ['1', '2', '1.0', '2.0']:
            gioi_tinh = str(int(float(v)))
            break

    # 6. LẮP RÁP LẠI VÀO DÒNG CHUẨN
    new_row = pd.Series(index=row.index, dtype=object)
    
    if pd.notna(ten_ch): new_row['HO_TEN_CHU_HO'] = ten_ch
    if pd.notna(ten_tv): new_row['HO_TEN_THANH_VIEN'] = ten_tv
    if pd.notna(ngay_sinh): new_row['NGAY_SINH'] = ngay_sinh
    if pd.notna(cccd): new_row['SO_CCCD'] = cccd
    if pd.notna(xa): new_row['XA'] = xa
    if pd.notna(gioi_tinh): new_row['GIOI_TINH'] = gioi_tinh
    
    # Suy luận lại Quan hệ
    if pd.notna(ten_ch) and pd.notna(ten_tv):
        new_row['QUANHE_CHUHO'] = '1' if ten_ch.strip() == ten_tv.strip() else '3'
        
    new_row['TINH'] = 'ĐẮK NÔNG'
    new_row['HUYEN'] = 'ĐĂK MIL'
    return new_row

def process_dakmil_ultimate_fix(input_filepath, output_filepath):
    print(f"{'='*60}")
    print(f"ĐANG CHẠY THUẬT TOÁN BÓC TÁCH VÀ DỌN RÁC ĐẮK MIL")
    print(f"{'='*60}")
    
    xls = pd.ExcelFile(input_filepath)
    df = pd.read_excel(xls, sheet_name=1)

    df.columns = df.columns.str.replace('\n', '').str.replace(' ', '').str.upper()
    df = df.rename(columns={'DANTOC': 'DANTOC', 'PHAN_LOAI_HO': 'PHAN_LOAI_HO', 'GIOI_TINH': 'GIOI_TINH'})
    
    cols_to_drop = [c for c in df.columns if 'UNNAMED' in str(c)]
    if cols_to_drop: df = df.drop(columns=cols_to_drop)
    df = df.astype(object)
    
    df_working = df.copy()

    # Xác định các dòng bị lỗi để nhờ AI vào cứu (Tỉnh bị rỗng, hoặc Tỉnh không phải Đắk Nông)
    mask_error = (~df_working['TINH'].astype(str).str.contains('ĐẮK NÔNG|DAK NONG|ĐĂK NÔNG', case=False, na=False))
    print(f"[+] Tìm thấy {mask_error.sum()} dòng bị mất Tỉnh / vỡ cấu trúc. Đang nhờ AI gắp và thả lại đúng cột...")
    
    # Gọi AI giải cứu các dòng lỗi
    df_working.loc[mask_error] = df_working.loc[mask_error].apply(ai_rescue_broken_row, axis=1)

    print("[+] Đang loại bỏ người chết và chuẩn hóa CCCD...")
    if 'DANTOC' in df_working.columns: df_working['DANTOC'] = df_working['DANTOC'].apply(normalize_dantoc)

    # Lọc người chết
    cccd_raw = df_working['SO_CCCD'].astype(str).str.strip().str.lower()
    ghi_chu_raw = df_working['GHI_CHU'].astype(str).str.strip().str.lower()
    is_dead = cccd_raw.str.contains('chết|mất|qua đời|từ trần|đã chết', regex=True, na=False) | ghi_chu_raw.str.contains('chết|mất|qua đời|từ trần|đã chết', regex=True, na=False)
    if is_dead.sum() > 0: df_working = df_working[~is_dead].copy()
    
    # -------------------------------------------------------------
    # TRÍCH XUẤT NGÀY SINH, THÁNG SINH, NĂM SINH THEO YÊU CẦU
    # -------------------------------------------------------------
    print("[+] Đang bóc tách Ngày sinh, Tháng sinh và Năm sinh...")
    # Bóc Năm
    years_from_ngaysinh = df_working['NGAY_SINH'].astype(str).str.extract(r'(\b(?:19|20)\d{2}\b)')[0]
    
    # Bóc Tháng (Bắt 2 số đứng ngay trước dấu / hoặc - cuối cùng)
    months_from_ngaysinh = df_working['NGAY_SINH'].astype(str).str.extract(r'(?:/|-)(\d{1,2})(?:/|-)(?:19|20)\d{2}')[0]
    
    # Bóc Ngày (Bắt 1-2 số đứng ở đầu dòng trước dấu / hoặc -)
    days_from_ngaysinh = df_working['NGAY_SINH'].astype(str).str.extract(r'^(\d{1,2})(?:/|-)')[0]

    df_working['NGAY'] = pd.to_numeric(days_from_ngaysinh, errors='coerce').astype('Int64')
    df_working['THANG'] = pd.to_numeric(months_from_ngaysinh, errors='coerce').astype('Int64')
    df_working['NAM_SINH'] = pd.to_numeric(years_from_ngaysinh, errors='coerce').astype('Int64')
    df_working['TUOI'] = 2023 - df_working['NAM_SINH']

    # Làm sạch CCCD
    def clean_cccd(val):
        v = re.sub(r'\D', '', str(val))
        if len(v) in [10, 11] and not v.startswith('0'): return v.zfill(12)
        if len(v) == 12: return v
        return np.nan

    df_working['SO_CCCD_CLEAN'] = df_working['SO_CCCD'].apply(clean_cccd)
    df_working['HAS_VALID_CCCD'] = np.where(df_working['SO_CCCD_CLEAN'].notna(), 1, 0)
    
    # Đánh ID_HO_GLOBAL
    is_chu_ho = (df_working['QUANHE_CHUHO'].astype(str).str.strip().isin(['1', '1.0'])) | \
                (df_working['HO_TEN_CHU_HO'].astype(str).str.strip().str.lower() == df_working['HO_TEN_THANH_VIEN'].astype(str).str.strip().str.lower())
    df_working['STT_HO'] = is_chu_ho.cumsum()
    df_working['STT_HO'] = df_working['STT_HO'].replace(0, np.nan).ffill().fillna(1).astype(int)
    df_working['ID_HO_GLOBAL'] = "DM_" + df_working['STT_HO'].astype(str)
    
    # Xóa cột thô
    cols_to_drop_final = ['NGAY_SINH', 'SO_CCCD', 'DC_DINHDANH', 'DC_CMND', 'STT']
    df_final = df_working.drop(columns=[c for c in cols_to_drop_final if c in df_working.columns])

    # Sắp xếp lại thứ tự cột cho đẹp mắt (Đưa Ngày, Tháng, Năm ra cạnh nhau)
    order = ['ID_HO_GLOBAL', 'HO_TEN_CHU_HO', 'HO_TEN_THANH_VIEN', 'QUANHE_CHUHO', 'GIOI_TINH', 
             'NGAY', 'THANG', 'NAM_SINH', 'TUOI', 'TINH', 'HUYEN', 'XA', 'DANTOC', 
             'PHAN_LOAI_HO', 'KET_QUA', 'GHI_CHU', 'SO_CCCD_CLEAN', 'HAS_VALID_CCCD']
    df_final = df_final[[c for c in order if c in df_final.columns]]

    df_final.to_excel(output_filepath, index=False)
    print(f"-> THÀNH CÔNG! Đã xuất file Đắk Mil chuẩn nhất tại: {output_filepath}")

if __name__ == "__main__":
    input_file = r"Dữ liệu chuẩn hóa\CẬP NHẬT 20.9.2023\HUYỆN DAK MIL.xlsx" 
    output_dir = "Cleaned_Data_All"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "HUYỆN DAK MIL_CLEANED.xlsx")
    
    process_dakmil_ultimate_fix(input_file, output_file)