import pandas as pd
import numpy as np

def generate_ml_dataset(input_filepath, output_filepath):
    print(f"{'='*60}")
    print("XÂY DỰNG TẬP DỮ LIỆU HUẤN LUYỆN (V2 - DATA IMPUTATION)")
    print(f"{'='*60}")
    
    print(f"1. ĐANG ĐỌC FILE NHÂN KHẨU: {input_filepath}")
    df = pd.read_csv(input_filepath, dtype={'SO_CCCD_CLEAN': str, 'ID_HO_GLOBAL': str, 'QUANHE_CHUHO': str}, low_memory=False)
    
    # -------------------------------------------------------------
    # 2. ĐIỀN KHUYẾT DỮ LIỆU TỪ SỚM (EARLY IMPUTATION)
    # -------------------------------------------------------------
    print("2. ĐANG TRÁM DỮ LIỆU BỊ TRỐNG (NULL/NaN)...")
    
    # 2.1 Trám Huyện bị thiếu dựa trên tiền tố của ID_HO_GLOBAL (VD: 'CJ_' -> Cư Jút)
    prefix_to_huyen = {
        'CJ': 'CƯ JUT', 'DM': 'ĐĂK MIL', 'DGL': 'ĐẮK GLONG', 
        'DRL': 'ĐẮK RLẤP', 'DS': 'ĐẮK SONG', 'KN': 'KRÔNG NÔ', 
        'TD': 'TUY ĐỨC', 'GN': 'GIA NGHĨA'
    }
    df['TEMP_PREFIX'] = df['ID_HO_GLOBAL'].str.extract(r'^([A-Z]+)_')[0]
    df['HUYEN'] = df['HUYEN'].fillna(df['TEMP_PREFIX'].map(prefix_to_huyen))
    
    # 2.2 Trám Xã (203 dòng bị trống ở Đắk Mil). Gán thành "CHƯA RÕ" để mô hình gom thành 1 nhóm an toàn.
    df['XA'] = df['XA'].fillna('CHƯA RÕ')
    
    # 2.3 Trám Phân loại hộ: Nếu trống tức là hộ bình thường (0)
    df['PHAN_LOAI_HO'] = pd.to_numeric(df['PHAN_LOAI_HO'], errors='coerce').fillna(0)
    
    # 2.4 Trám Tuổi, Giới tính, Dân tộc bằng Trung vị (Median) và Yếu vị (Mode) của Huyện đó
    df['TUOI'] = pd.to_numeric(df['TUOI'], errors='coerce')
    df['TUOI'] = df.groupby('HUYEN')['TUOI'].transform(lambda x: x.fillna(x.median()))
    
    df['GIOI_TINH'] = pd.to_numeric(df['GIOI_TINH'], errors='coerce')
    df['GIOI_TINH'] = df.groupby('HUYEN')['GIOI_TINH'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 1))
    
    df['DANTOC'] = pd.to_numeric(df['DANTOC'], errors='coerce').fillna(1) # Rỗng thì gán mặc định là Kinh (1)

    # Dọn dẹp sơ bộ cột Quan hệ chủ hộ
    df['QUANHE_CHUHO'] = df['QUANHE_CHUHO'].astype(str).str.replace('.0', '', regex=False)
    df.loc[~df['QUANHE_CHUHO'].isin(['1', '2', '3', '4', '5']), 'QUANHE_CHUHO'] = np.nan
    df['QUANHE_CHUHO'] = pd.to_numeric(df['QUANHE_CHUHO'], errors='coerce')
    
    # -------------------------------------------------------------
    # 3. TRÍCH XUẤT THÔNG TIN CỦA CHỦ HỘ
    # -------------------------------------------------------------
    chu_ho = df[df['QUANHE_CHUHO'] == 1].copy()
    chu_ho_features = chu_ho[['ID_HO_GLOBAL', 'GIOI_TINH', 'TUOI', 'DANTOC']].rename(columns={
        'GIOI_TINH': 'GIOI_TINH_CHU_HO',
        'TUOI': 'TUOI_CHU_HO',
        'DANTOC': 'DANTOC_CHU_HO'
    })
    chu_ho_features = chu_ho_features.drop_duplicates(subset=['ID_HO_GLOBAL'])
    
    # -------------------------------------------------------------
    # 4. ĐẾM VÀ PHÂN LOẠI CẤU TRÚC GIA ĐÌNH
    # -------------------------------------------------------------
    print("3. ĐANG GOM NHÓM (GROUPBY) VÀ ĐẾM NGƯỜI PHỤ THUỘC...")
    df['IS_TRE_EM'] = np.where(df['TUOI'] < 18, 1, 0)
    df['IS_NGUOI_GIA'] = np.where(df['TUOI'] > 60, 1, 0)
    df['IS_LAO_DONG'] = np.where((df['TUOI'] >= 18) & (df['TUOI'] <= 60), 1, 0)
    df['HAS_VALID_CCCD'] = pd.to_numeric(df['HAS_VALID_CCCD'], errors='coerce').fillna(0)
    
    agg_funcs = {
        'ID_HO_GLOBAL': 'count',      # QUY_MO_HO
        'IS_TRE_EM': 'sum',
        'IS_NGUOI_GIA': 'sum',
        'IS_LAO_DONG': 'sum',
        'HAS_VALID_CCCD': 'sum',
        'PHAN_LOAI_HO': 'max',        # Lấy giá trị cao nhất (vd có 1 người nghèo là cả hộ nghèo)
        'HUYEN': 'first',
        'XA': 'first'
    }
    
    ho_gia_dinh = df.groupby('ID_HO_GLOBAL').agg(agg_funcs).rename(columns={'ID_HO_GLOBAL': 'QUY_MO_HO'})
    ho_gia_dinh.index.name = 'ID_HO_GLOBAL_IDX' # Tránh lỗi trùng lặp cột index
    ho_gia_dinh = ho_gia_dinh.reset_index().rename(columns={
        'ID_HO_GLOBAL_IDX': 'ID_HO_GLOBAL',
        'IS_TRE_EM': 'SO_TRE_EM',
        'IS_NGUOI_GIA': 'SO_NGUOI_GIA',
        'IS_LAO_DONG': 'SO_LAO_DONG',
        'HAS_VALID_CCCD': 'SO_NGUOI_CO_CCCD'
    })
    
    final_df = pd.merge(ho_gia_dinh, chu_ho_features, on='ID_HO_GLOBAL', how='left')
    
    # Trám một lần nữa cho các hộ KHÔNG CÓ người nào đánh dấu là Chủ hộ (QUANHE_CHUHO == 1)
    # Lấy thông tin của người lớn tuổi nhất trong hộ đó làm Chủ hộ đại diện
    missing_chu_ho = final_df['TUOI_CHU_HO'].isna()
    if missing_chu_ho.sum() > 0:
        idx_oldest = df.groupby('ID_HO_GLOBAL')['TUOI'].idxmax()
        oldest_members = df.loc[idx_oldest, ['ID_HO_GLOBAL', 'GIOI_TINH', 'TUOI', 'DANTOC']]
        final_df.loc[missing_chu_ho, 'TUOI_CHU_HO'] = final_df.loc[missing_chu_ho, 'ID_HO_GLOBAL'].map(oldest_members.set_index('ID_HO_GLOBAL')['TUOI'])
        final_df.loc[missing_chu_ho, 'GIOI_TINH_CHU_HO'] = final_df.loc[missing_chu_ho, 'ID_HO_GLOBAL'].map(oldest_members.set_index('ID_HO_GLOBAL')['GIOI_TINH'])
        final_df.loc[missing_chu_ho, 'DANTOC_CHU_HO'] = final_df.loc[missing_chu_ho, 'ID_HO_GLOBAL'].map(oldest_members.set_index('ID_HO_GLOBAL')['DANTOC'])

    # -------------------------------------------------------------
    # 5. TẠO CÁC FEATURES NÂNG CAO CHO MACHINE LEARNING
    # -------------------------------------------------------------
    print("4. ĐANG TẠO CÁC FEATURES TỶ LỆ & NHÓM LÕI TỰ ĐỘNG...")
    final_df['TY_LE_PHU_THUOC'] = ((final_df['SO_TRE_EM'] + final_df['SO_NGUOI_GIA']) / final_df['QUY_MO_HO']).round(3)
    final_df['TY_LE_CO_CCCD'] = (final_df['SO_NGUOI_CO_CCCD'] / final_df['QUY_MO_HO']).round(3)
    
    def phan_loai_gia_dinh(row):
        if row['QUY_MO_HO'] == 1: return 'Độc thân/Neo đơn'
        elif row['SO_LAO_DONG'] <= 1 and row['SO_TRE_EM'] > 0: return 'Đơn thân nuôi con'
        elif row['SO_TRE_EM'] == 0 and row['SO_NGUOI_GIA'] > 0 and row['SO_LAO_DONG'] == 0: return 'Người già nương tựa'
        elif row['SO_LAO_DONG'] >= 2: return 'Gia đình hạt nhân/Mở rộng'
        else: return 'Khác'
            
    final_df['LOAI_HINH_GIA_DINH'] = final_df.apply(phan_loai_gia_dinh, axis=1)
    
    # Target Encoding
    xa_stats = final_df.groupby(['HUYEN', 'XA'])['PHAN_LOAI_HO'].apply(lambda x: (x.isin([1, 2]).sum() / len(x))).reset_index(name='TY_LE_NGHEO_CUA_XA')
    xa_stats['TY_LE_NGHEO_CUA_XA'] = xa_stats['TY_LE_NGHEO_CUA_XA'].round(3)
    final_df = pd.merge(final_df, xa_stats, on=['HUYEN', 'XA'], how='left')
    
    # -------------------------------------------------------------
    # 6. XUẤT TẬP DỮ LIỆU SẠCH 100%
    # -------------------------------------------------------------
    # Ép kiểu nguyên lần cuối
    int_cols = ['QUY_MO_HO', 'SO_LAO_DONG', 'SO_TRE_EM', 'SO_NGUOI_GIA', 'GIOI_TINH_CHU_HO', 'TUOI_CHU_HO', 'DANTOC_CHU_HO', 'PHAN_LOAI_HO']
    final_df[int_cols] = final_df[int_cols].astype(int)

    order = [
        'ID_HO_GLOBAL', 'HUYEN', 'XA', 'QUY_MO_HO', 'SO_LAO_DONG', 'SO_TRE_EM', 'SO_NGUOI_GIA',
        'TY_LE_PHU_THUOC', 'GIOI_TINH_CHU_HO', 'TUOI_CHU_HO', 'DANTOC_CHU_HO', 
        'LOAI_HINH_GIA_DINH', 'TY_LE_CO_CCCD', 'TY_LE_NGHEO_CUA_XA', 'PHAN_LOAI_HO'
    ]
    final_df = final_df[[c for c in order if c in final_df.columns]]
    
    final_df.to_csv(output_filepath, index=False, encoding='utf-8-sig')
    print(f"-> THÀNH CÔNG! Đã xuất {len(final_df):,} Hộ gia đình KHÔNG CÒN LỖ HỔNG DỮ LIỆU ra file: {output_filepath}")

if __name__ == "__main__":
    input_master = "DAK_NONG_MASTER_POPULATION.csv" 
    output_ml_dataset = "DAK_NONG_ML_DATASET.csv" 
    
    generate_ml_dataset(input_master, output_ml_dataset)