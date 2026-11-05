import glob
import pandas as pd
import os

input_dir = "Cleaned_Data_Master"
output_dir = "Household_Data"

pattern = os.path.join(input_dir, '*_CLEANED.xlsx')
file_list = [f for f in glob.glob(pattern) if not os.path.basename(f).startswith('~$')]

for file in file_list:
  df = pd.read_excel(file)

  # 1. Tính quy mô hộ (Tổng số thành viên trong hộ)
  df_size = df.groupby("ID_HO_GLOBAL").size().reset_index(name="QUY_MO_HO")

  # 2. Lấy thông tin Chủ hộ
  df_chuho = df[df["QUANHE_CHUHO"] == 1.0][
      ["ID_HO_GLOBAL", "GIOI_TINH", "TUOI", "DANTOC", "PHAN_LOAI_HO", "HUYEN", "XA"]
  ].copy()
  df_chuho.rename(
      columns={
          "GIOI_TINH": "GIOI_TINH_CHU_HO",
          "TUOI": "TUOI_CHU_HO",
          "DANTOC": "DANTOC_CHU_HO",
      },
      inplace=True,
  )


  # 3. Hàm xác định Lao động chính và Người phụ thuộc theo giới tính và độ tuổi
  def check_labor(row):
    tuoi = row["TUOI"]
    gioi_tinh = row["GIOI_TINH"]

    if pd.isna(tuoi):
      return pd.Series([0, 0])

    # Dưới 15 tuổi là người phụ thuộc
    if tuoi < 15:
      return pd.Series([0, 1])

    # Nam: từ 15 đến 62 tuổi là lao động chính
    if gioi_tinh == 1:
      if 15 <= tuoi <= 62:
        return pd.Series([1, 0])
      else:
        return pd.Series([0, 1])  # Trên 62 tuổi là phụ thuộc (người già)

    # Nữ: từ 15 đến 60 tuổi là lao động chính
    elif gioi_tinh == 2:
      if 15 <= tuoi <= 60:
        return pd.Series([1, 0])
      else:
        return pd.Series([0, 1])  # Trên 60 tuổi là phụ thuộc

    else:
      # Trường hợp khuyết thiếu giới tính, áp dụng mặc định chung 15-60
      if 15 <= tuoi <= 60:
        return pd.Series([1, 0])
      else:
        return pd.Series([0, 1])


  # Áp dụng hàm phân loại cho từng thành viên
  df[["LAO_DONG_CHINH", "PHU_THUOC"]] = df.apply(check_labor, axis=1)

  # Gom nhóm tính tổng số lao động chính và số người phụ thuộc cho từng hộ
  df_labor = (
      df.groupby("ID_HO_GLOBAL")[["LAO_DONG_CHINH", "PHU_THUOC"]]
      .sum()
      .reset_index()
  )

  # Gộp các đặc trưng lại với nhau thành bộ dữ liệu cấp Hộ
  df_household = df_size.merge(df_chuho, on="ID_HO_GLOBAL", how="left")
  df_household = df_household.merge(df_labor, on="ID_HO_GLOBAL", how="left")

  # Lưu kết quả file cấp hộ cho từng huyện
  filename = os.path.basename(file)
  output_filename = os.path.join(
      output_dir, filename.replace("_CLEANED.xlsx", "_HOUSEHOLD.xlsx")
  )
  df_household.to_excel(output_filename, index=False)
  print(
      f"Đã xử lý xong: {output_filename} - Tổng số hộ sau khi gom nhóm:"
      f" {len(df_household)}"
  )