# Dự án Phân tích & Tiền xử lý Dữ liệu An sinh Xã hội tỉnh Đắk Nông

## 1. Tổng quan Dự án (Project Overview)

Dự án này thực hiện quy trình chuẩn hóa, làm sạch và làm giàu dữ liệu (Data Cleaning, Normalization & Feature Engineering) cho tập dữ liệu hành chính - an sinh xã hội cấp huyện của tỉnh Đắk Nông (dữ liệu cập nhật kỳ rà soát hộ nghèo, hộ cận nghèo).

Quá trình xử lý đi từ nguồn dữ liệu thô dạng Excel với nhiều lỗi cấu trúc vật lý nghiêm trọng (ô bị xóa ngẫu nhiên, trượt cột, trộn lẫn kiểu dữ liệu, mất số 0 đầu chuỗi CCCD), qua các giai đoạn giải cứu dữ liệu bằng thuật toán bóc tách thông minh, xử lý thực thể (Entity Resolution) và khử trùng lặp toàn cục, sau đó rẽ nhánh thành 2 luồng phục vụ các mục tiêu chuyên biệt:

1. **Luồng BI & Data Warehouse (DWH):** Gom nhóm cấp hộ gia đình, tính toán chỉ số lao động theo Bộ luật Lao động, điền khuyết và chuẩn hóa thành mô hình **Star Schema** (Lược đồ hình sao gồm 1 bảng Fact và 3 bảng Dimension) sẵn sàng nạp vào PostgreSQL và trực quan hóa chuyên sâu trên Power BI.
2. **Luồng Machine Learning (AI):** Tổng hợp từ dữ liệu nhân khẩu đã khử trùng lặp toàn diện, trích xuất đặc trưng chủ hộ, phân loại cấu trúc gia đình, tính toán tỷ lệ phụ thuộc, tỷ lệ phủ CCCD và Target Encoding tỷ lệ nghèo cấp xã để tạo tập dữ liệu huấn luyện (Training Dataset) cho các mô hình phân loại dự đoán nghèo đói (XGBoost, Random Forest).

---

## 2. Cấu trúc Thư mục Thực tế (Project Directory Structure)

```text
Intern/
│
├── .venv/                                   # Môi trường ảo Python
│
├── Dữ liệu chuẩn hóa/CẬP NHẬT 20.9.2023/    # Nguồn dữ liệu thô ban đầu (8 huyện/thành phố + 1 file tổng hợp)
│   ├── HUYỆN CƯ JUT.xlsx                    # 11.844 dòng thô
│   ├── HUYỆN DAK MIL.xlsx                   # Sheet thô vỡ cấu trúc 'DM 31-8-2023' (6.661 dòng)
│   ├── HUYỆN KRÔNG NÔ.xlsx                  # 15.095 dòng (lỗi lệch cột Tỉnh/Xã và Ngày sinh)
│   ├── HUYỆN ĐẮK RLẤP.xlsx                  # 4.242 dòng
│   ├── HUYỆN ĐẮK SONG.xlsx                  # 9.029 dòng
│   ├── HUYỆN TUY ĐỨC.xlsx                   # 22.182 dòng
│   ├── Huyện Đắk Glong.xlsx                 # 37.428 dòng
│   ├── TP GIA NGHĨA.xlsx                    # 970 dòng
│   └── tổng hợp.xlsx                        # File số liệu tổng hợp báo cáo hành chính
│
├── Cleaned_Data_Master/                     # Chứa 8 file cấp Huyện đã qua nắn cột & làm sạch chuẩn (_CLEANED.xlsx)
│   ├── HUYỆN CƯ JUT_CLEANED.xlsx            # 11.828 nhân khẩu (18 cột)
│   ├── HUYỆN DAK MIL_CLEANED.xlsx           # 6.658 nhân khẩu (18 cột)
│   ├── HUYỆN KRÔNG NÔ_CLEANED.xlsx          # 15.090 nhân khẩu (18 cột)
│   ├── HUYỆN ĐẮK RLẤP_CLEANED.xlsx          # 4.236 nhân khẩu (18 cột)
│   ├── HUYỆN ĐẮK SONG_CLEANED.xlsx          # 9.014 nhân khẩu (18 cột)
│   ├── HUYỆN TUY ĐỨC_CLEANED.xlsx           # 22.176 nhân khẩu (18 cột)
│   ├── Huyện Đắk Glong_CLEANED.xlsx         # 37.427 nhân khẩu (18 cột)
│   └── TP GIA NGHĨA_CLEANED.xlsx            # 969 nhân khẩu (18 cột)
│
├── Household_Data/                          # Chứa 8 file tổng hợp đặc trưng cấp Hộ gia đình từng huyện (_HOUSEHOLD.xlsx)
│   ├── HUYỆN CƯ JUT_HOUSEHOLD.xlsx          # 2.533 hộ
│   ├── HUYỆN DAK MIL_HOUSEHOLD.xlsx         # 1.302 hộ
│   ├── HUYỆN KRÔNG NÔ_HOUSEHOLD.xlsx        # 3.295 hộ
│   ├── HUYỆN ĐẮK RLẤP_HOUSEHOLD.xlsx        # 1.086 hộ
│   ├── HUYỆN ĐẮK SONG_HOUSEHOLD.xlsx        # 3.153 hộ
│   ├── HUYỆN TUY ĐỨC_HOUSEHOLD.xlsx         # 4.662 hộ
│   ├── Huyện Đắk Glong_HOUSEHOLD.xlsx       # 7.115 hộ
│   └── TP GIA NGHĨA_HOUSEHOLD.xlsx          # 241 hộ
│
├── Star_Schema_DB_Ready/                    # 4 file CSV mô hình Star Schema sẵn sàng cho PostgreSQL & Power BI
│   ├── Fact_Household.csv                   # 23.387 dòng, 9 cột (Bảng sự kiện cấp Hộ)
│   ├── Dim_Geography.csv                    # 143 dòng, 3 cột (Bảng chiều Địa lý: GEO_ID, HUYEN, XA)
│   ├── Dim_Demographic.csv                  # 27 dòng, 2 cột (Bảng chiều Dân tộc: DEMO_ID, DEMO_NAME)
│   └── Dim_Household_Status.csv             # 3 dòng, 2 cột (Bảng chiều Trạng thái: STATUS_ID, STATUS_NAME)
│
├── Code/                                    # Kịch bản Python xử lý dữ liệu và xây dựng kho dữ liệu
│   ├── 1_Dak_Mil.py                         # Giải cứu và dọn rác cấu trúc vỡ nát đặc thù cho Đắk Mil
│   ├── 1_Krong_No.py                        # Sửa lỗi trôi cột Xã sang Tỉnh và lệch Ngày sinh cho Krông Nô
│   ├── 1_PreprocessingMaster.py             # Pipeline tiền xử lý vạn năng chạy chuẩn hóa cho 6 huyện/TP còn lại
│   ├── 2_MergeAndDeduplicate.py             # Hợp nhất 8 file sạch, xử lý số 0 CCCD, khử trùng lặp thực thể toàn tỉnh
│   ├── 3_Household.py                       # Phân loại lao động theo luật, tính phụ thuộc, gom nhóm thành cấp Hộ
│   ├── 4_FillNull.py                        # Hợp nhất 8 file hộ, điền khuyết (Imputation) dữ liệu thiếu
│   └── 5_Split_Star_Schema.py               # Tách bảng Fact và 3 bảng Dimension chuẩn hóa mô hình hình sao
│
├── Code ML/                                 # Kịch bản Python chuẩn bị dữ liệu phục vụ Trí tuệ Nhân tạo
│   └── Generate_ML_Dataset.py               # Feature Engineering từ Master Population sang Dataset cấp Hộ cho ML
│
├── DAK_NONG_MASTER_POPULATION.csv           # File Tổng 101.623 nhân khẩu toàn tỉnh đã sạch & khử trùng (Kết quả Bước 2)
├── DAK_NONG_HOUSEHOLDS_MASTER.csv           # File Tổng 23.387 hộ gia đình toàn tỉnh đã điền khuyết (Kết quả Bước 4)
└── DAK_NONG_ML_DATASET.csv                  # File Dataset 22.698 hộ sạch 100% kèm 15 đặc trưng cho ML (Kết quả Bước 6)
```

---

## 3. Quy trình Thực thi Chi tiết (Pipeline Execution Workflow)

Quy trình xử lý được phân tách rõ ràng qua 6 bước chính tuần tự:

```
[Dữ liệu thô Excel]
        │
        ▼ (Bước 1: 1_Dak_Mil.py, 1_Krong_No.py, 1_PreprocessingMaster.py)
[Cleaned_Data_Master/*_CLEANED.xlsx] (107.398 dòng thô đã nắn chuẩn)
        │
        ├────────────────────────────────────────────────────────────────────────┐
        ▼ (Bước 2: 2_MergeAndDeduplicate.py)                                     ▼ (Bước 3: 3_Household.py)
[DAK_NONG_MASTER_POPULATION.csv] (101.623 nhân khẩu)                     [Household_Data/*_HOUSEHOLD.xlsx]
        │                                                                        │
        ▼ (Bước 6: Code ML/Generate_ML_Dataset.py)                               ▼ (Bước 4: 4_FillNull.py)
[DAK_NONG_ML_DATASET.csv] (22.698 hộ, 15 features)                       [DAK_NONG_HOUSEHOLDS_MASTER.csv] (23.387 hộ)
                                                                                 │
                                                                                 ▼ (Bước 5: 5_Split_Star_Schema.py)
                                                                         [Star_Schema_DB_Ready/] (1 Fact, 3 Dim)
```

---

### Bước 1: Tiền xử lý & Nắn cột cấp cơ sở (Tiền tố `1_`)

Dữ liệu thô gặp nhiều dị tật kỹ thuật do người nhập liệu: ô bị dịch trái/phải, xóa cột ngẫu nhiên, ngày sinh lẫn vào cột quan hệ, CCCD bị Excel đổi thành dạng số khoa học (`6.71E+10`), số 0 đầu bị xóa mất.

* **`Code/1_Dak_Mil.py`**:
  * Đọc sheet dữ liệu `DM 31-8-2023` (bỏ qua sheet rỗng `foxz`).
  * Sử dụng thuật toán bóc tách thông minh dựa trên biểu thức chính quy (`ai_rescue_broken_row`) để duyệt từng dòng lỗi (dòng thiếu Tỉnh hoặc Tỉnh không phải Đắk Nông):
    * Tự động quét và nhặt tên Xã (dựa trên các tiền tố `ĐẮK`, `DAK`, `ĐĂK`).
    * Nhận diện Ngày sinh (chuỗi chứa năm `19xx`/`20xx`, tự sửa lỗi gõ 2 dấu gạch chéo `//`, hoặc chuyển đổi ngày dạng số nguyên Serial của Excel từ 10.000 đến 50.000 về ngày chuẩn).
    * Bóc tách số CCCD/Định danh (chuỗi 8-12 chữ số, giải mã chuỗi `E+10`/`E+09`).
    * Nhận diện họ tên Chủ hộ và Thành viên (chuỗi chữ dài hơn 4 ký tự không chứa số).
    * Nhận diện giới tính (số 1 hoặc 2 đứng đơn lẻ).
    * Tái cấu trúc lại dòng và suy luận quan hệ chủ hộ (nếu tên thành viên trùng tên chủ hộ thì gán mã `1`, khác thì gán mã `3`).
  * Chuẩn hóa mã dân tộc (34 dân tộc theo bảng tra cứu `DANTOC_MAP`), lọc bỏ các dòng ghi chú người đã mất (`chết`, `mất`, `qua đời`, `từ trần`).
  * Tách riêng 3 trường: `NGAY`, `THANG`, `NAM_SINH` và tính `TUOI = 2023 - NAM_SINH`.
  * Khôi phục 12 chữ số CCCD bằng hàm `zfill(12)`, tạo cờ `HAS_VALID_CCCD`.
  * Đánh mã định danh hộ gia đình toàn cục `ID_HO_GLOBAL` với tiền tố `DM_` (ví dụ: `DM_1`, `DM_2`,...).
  * Xuất kết quả ra `Cleaned_Data_Master/HUYỆN DAK MIL_CLEANED.xlsx` (6.658 nhân khẩu).

* **`Code/1_Krong_No.py`**:
  * Khắc phục lỗi trượt cột nghiêm trọng tại các dòng 11.009 - 11.360 (và nhóm dòng 2.000+): cột Tỉnh bị mất khiến Xã nhảy sang Tỉnh, Huyện nhảy sang Dân tộc, Dân tộc nhảy sang Kết quả. Thuật toán phát hiện điều kiện bất thường và đẩy ngược các cột về đúng vị trí, đồng thời gán cứng lại `TINH = 'ĐẮK NÔNG'`, `HUYEN = 'KRÔNG NÔ'`.
  * Khắc phục lỗi Ngày sinh trượt sang cột `QUANHE_CHUHO`: phát hiện chuỗi ngày tháng nằm trong cột quan hệ, chuyển giá trị về `NGAY_SINH`, đồng thời khôi phục lại quan hệ chủ hộ thông qua so sánh họ tên thành viên và chủ hộ.
  * Bổ sung tính năng giải mã năm sinh từ 12 số CCCD: bóc tách mã thế kỷ (vị trí thứ 4) và 2 số năm sinh (vị trí 5-6) để bù đắp các dòng bị khuyết năm sinh.
  * Đánh mã định danh hộ gia đình `ID_HO_GLOBAL` với tiền tố `KN_`.
  * Xuất kết quả ra `Cleaned_Data_Master/HUYỆN KRÔNG NÔ_CLEANED.xlsx` (15.090 nhân khẩu).

* **`Code/1_PreprocessingMaster.py`**:
  * Kịch bản tiền xử lý tổng hợp (Universal Pipeline) kế thừa toàn bộ cơ chế cứu dòng lỗi của Đắk Mil và Krông Nô.
  * Tự động chạy hàng loạt cho 6 đơn vị hành chính còn lại với các tiền tố định danh tương ứng:
    * Huyện Cư Jút (`CJ`) -> `HUYỆN CƯ JUT_CLEANED.xlsx` (11.828 nhân khẩu)
    * Huyện Đắk Glong (`DGL`) -> `Huyện Đắk Glong_CLEANED.xlsx` (37.427 nhân khẩu)
    * Huyện Đắk R'lấp (`DRL`) -> `HUYỆN ĐẮK RLẤP_CLEANED.xlsx` (4.236 nhân khẩu)
    * Huyện Đắk Song (`DS`) -> `HUYỆN ĐẮK SONG_CLEANED.xlsx` (9.014 nhân khẩu)
    * Huyện Tuy Đức (`TD`) -> `HUYỆN TUY ĐỨC_CLEANED.xlsx` (22.176 nhân khẩu)
    * TP Gia Nghĩa (`GN`) -> `TP GIA NGHĨA_CLEANED.xlsx` (969 nhân khẩu)
  * Toàn bộ 8 file đầu ra đều thống nhất cấu trúc 18 cột chuẩn.

---

### Bước 2: Hợp nhất & Khử trùng lặp Toàn cục (`Code/2_MergeAndDeduplicate.py`)

Thực hiện giải quyết thực thể (Entity Resolution) trên phạm vi toàn tỉnh từ 8 file sạch:

1. **Khôi phục số 0 đầu chuỗi CCCD:** Ép kiểu String và sử dụng `.str.zfill(12)` để sửa triệt để việc Pandas/Excel tự ý cắt mất số 0 đầu chuỗi CCCD.
2. **Chuẩn hóa chuỗi họ tên:** Chuyển viết hoa, loại bỏ toàn bộ khoảng trắng thừa bằng regex.
3. **Phát hiện và loại bỏ CCCD rác:** Thống kê số lượng tên người khác nhau gắn với cùng 1 số CCCD. Những số CCCD gán cho trên 2 người khác tên được xác định là dữ liệu rác (hoặc mượn CCCD) và được đưa về `NaN`.
4. **Khử trùng lặp thực thể (Deduplication):**
   * Đối với nhân khẩu có CCCD hợp lệ, thực hiện sắp xếp ưu tiên bản ghi có độ tin cậy cao nhất: Ưu tiên người là Chủ hộ (`QUANHE_CHUHO == 1`), ưu tiên bản ghi có trạng thái nghèo/cận nghèo (`PHAN_LOAI_HO` bằng 1 hoặc 2) trước trạng thái thường.
   * Tiến hành khử trùng theo `SO_CCCD_CLEAN`, giữ lại bản ghi chuẩn đầu tiên.
5. **Gom nhóm gia đình bằng Sắp xếp tự nhiên (Natural Sort):**
   * Tách tiền tố huyện (`TEMP_PREFIX`) và số thứ tự hộ dạng số nguyên (`TEMP_HID`) từ `ID_HO_GLOBAL`.
   * Sắp xếp theo thứ tự toán học tự nhiên: Huyện -> Số thứ tự hộ (1, 2, ..., 10, 11 thay vì 1, 10, 11, 2) -> Quan hệ chủ hộ. Đảm bảo toàn bộ thành viên trong cùng một hộ luôn đứng liền kề nhau với chủ hộ ở dòng đầu tiên.
6. **Bảo toàn số 0 khi lưu file CSV:** Thêm tiền tố tab `\t` trước chuỗi CCCD để các công cụ như Excel không bao giờ chuyển chuỗi thành số khi mở.
7. **Kết quả:** Xuất ra file **`DAK_NONG_MASTER_POPULATION.csv`** gồm **101.623 nhân khẩu** toàn tỉnh với 18 cột thuộc tính hoàn chỉnh.

---

### Bước 3: Tính toán Đặc trưng Cấp Hộ gia đình (`Code/3_Household.py`)

Chuyển đổi dữ liệu từ cấp nhân khẩu sang cấp hộ gia đình trên từng huyện trong `Cleaned_Data_Master/`:

1. **Tính quy mô hộ (`QUY_MO_HO`):** Đếm tổng số nhân khẩu theo từng `ID_HO_GLOBAL`.
2. **Trích xuất thông tin Chủ hộ:** Lọc các bản ghi có `QUANHE_CHUHO == 1.0` để lấy: `GIOI_TINH_CHU_HO`, `TUOI_CHU_HO`, `DANTOC_CHU_HO`, `PHAN_LOAI_HO`, `HUYEN`, `XA`.
3. **Phân loại Lao động theo Bộ luật Lao động Việt Nam (`check_labor`):**
   * Trẻ em (< 15 tuổi): Tính là Người phụ thuộc (`PHU_THUOC = 1`, `LAO_DONG_CHINH = 0`).
   * Nam giới (15 đến 62 tuổi): Tính là Lao động chính (`LAO_DONG_CHINH = 1`, `PHU_THUOC = 0`); trên 62 tuổi tính là Người phụ thuộc/Người già.
   * Nữ giới (15 đến 60 tuổi): Tính là Lao động chính (`LAO_DONG_CHINH = 1`, `PHU_THUOC = 0`); trên 60 tuổi tính là Người phụ thuộc/Người già.
   * Khuyết thiếu thông tin giới tính: Áp dụng khung mặc định chung từ 15 đến 60 tuổi là lao động chính.
4. **Gom nhóm và tổng hợp:** Tính tổng số lao động chính và tổng số người phụ thuộc cho từng hộ gia đình.
5. **Kết quả:** Xuất 8 file Excel tương ứng vào thư mục **`Household_Data/`** (`*_HOUSEHOLD.xlsx`) với tổng cộng **23.387 hộ gia đình**.

---

### Bước 4: Hợp nhất Hộ & Điền khuyết Dữ liệu (`Code/4_FillNull.py`)

Gộp 8 file từ thư mục `Household_Data/` và tiến hành xử lý dữ liệu khuyết (Imputation) trước khi phân nhánh:

1. **Phân loại hộ (`PHAN_LOAI_HO`):** Điền giá trị `0` cho các ô trống (đại diện cho Hộ bình thường hoặc đã thoát nghèo).
2. **Nội suy Huyện & Xã:**
   * Cột `HUYEN` bị trống được suy luận tự động từ tiền tố của `ID_HO_GLOBAL` (bảng ánh xạ: `CJ` -> CƯ JUT, `DM` -> ĐĂK MIL, `DGL` -> ĐẮK GLONG, `DRL` -> ĐẮK RLẤP, `DS` -> ĐẮK SONG, `KN` -> KRÔNG NÔ, `TD` -> TUY ĐỨC, `GN` -> GIA NGHĨA).
   * Cột `XA` bị trống được gán giá trị `"CHƯA RÕ"` để tránh lỗi Null trên Dashboard Power BI và tránh tạo nhóm rác.
3. **Điền khuyết Tuổi và Giới tính Chủ hộ:**
   * `TUOI_CHU_HO`: Điền bằng giá trị **Trung vị (Median)** của huyện tương ứng.
   * `GIOI_TINH_CHU_HO`: Điền bằng giá trị **Yếu vị (Mode)** của huyện tương ứng (mặc định bằng 1 - Nam nếu không tìm thấy mode).
4. **Điền khuyết Dân tộc:** Gán giá trị mặc định là `1` (Dân tộc Kinh - nhóm chiếm đa số).
5. **Kết quả:** Xuất ra file **`DAK_NONG_HOUSEHOLDS_MASTER.csv`** gồm **23.387 hộ gia đình** và 10 cột thuộc tính, dữ liệu đầy đủ không còn ô khuyết.

---

### Bước 5: Tách Lược đồ Hình sao Star Schema cho BI (`Code/5_Split_Star_Schema.py`)

Đọc file `DAK_NONG_HOUSEHOLDS_MASTER.csv` và bóc tách thành mô hình quan hệ hình sao phục vụ nạp vào Data Warehouse và Power BI:

1. **Bảng chiều Trạng thái Hộ (`Dim_Household_Status.csv` - 3 dòng):**
   * `STATUS_ID`: Khóa chính (0, 1, 2).
   * `STATUS_NAME`: Tên trạng thái (`Bình thường/Khác`, `Hộ nghèo`, `Hộ cận nghèo`).
2. **Bảng chiều Dân tộc (`Dim_Demographic.csv` - 27 dòng):**
   * Ánh xạ mã số dân tộc thành tên dân tộc tương ứng theo danh mục chuẩn (Kinh, Tày, Thái, Hoa, Khmer, Mường, Nùng, Hmông, Dao, Gia Rai, Ê Đê, M'Nông,...). Các mã không nằm trong danh mục chuẩn được gom nhóm thành `Khác`.
   * `DEMO_ID`: Khóa chính.
   * `DEMO_NAME`: Tên dân tộc.
3. **Bảng chiều Địa lý (`Dim_Geography.csv` - 143 dòng):**
   * Bóc tách các cặp duy nhất giữa `HUYEN` và `XA`.
   * Tự động sinh khóa đại diện `GEO_ID` từ `G1` đến `G143`.
   * `GEO_ID`: Khóa chính.
   * `HUYEN`: Tên Huyện/Thành phố.
   * `XA`: Tên Xã/Phường/Thị trấn.
4. **Bảng sự kiện Hộ gia đình (`Fact_Household.csv` - 23.387 dòng):**
   * Chỉ giữ lại các chỉ số đo lường (Measures) và các khóa ngoại (Foreign Keys):
     * Khóa/Mã định danh: `ID_HO_GLOBAL`.
     * Khóa ngoại: `STATUS_ID`, `DEMO_ID`, `GEO_ID`.
     * Chỉ số đo lường: `QUY_MO_HO`, `LAO_DONG_CHINH`, `PHU_THUOC`, `TUOI_CHU_HO`, `GIOI_TINH_CHU_HO`.
5. **Kết quả:** Lưu 4 file CSV vào thư mục **`Star_Schema_DB_Ready/`**.

---

### Bước 6: Feature Engineering cho Machine Learning (`Code ML/Generate_ML_Dataset.py`)

Kịch bản xây dựng bộ đặc trưng độc lập cho mô hình phân loại dự đoán hộ nghèo. Kịch bản này đọc trực tiếp từ **`DAK_NONG_MASTER_POPULATION.csv`** (tập dữ liệu nhân khẩu đã khử trùng lặp toàn diện ở Bước 2):

1. **Early Imputation (Điền khuyết sớm):**
   * Trám Huyện từ tiền tố ID, Xã trống gán `"CHƯA RÕ"`.
   * Phân loại hộ trống điền `0`.
   * Tuổi và Giới tính khuyết được trám bằng Median và Mode của từng huyện.
   * Dân tộc khuyết được điền `1` (Kinh).
2. **Xử lý Hộ không có Chủ hộ:**
   * Với các hộ không có bản ghi nào mang `QUANHE_CHUHO == 1`, thuật toán tự động tìm **thành viên lớn tuổi nhất trong hộ** và lấy thông tin người này làm chủ hộ đại diện.
3. **Gom cụm và Trích xuất chỉ số cấu trúc hộ:**
   * `QUY_MO_HO`: Tổng số thành viên.
   * `SO_TRE_EM`: Số người dưới 18 tuổi trong hộ.
   * `SO_NGUOI_GIA`: Số người trên 60 tuổi trong hộ.
   * `SO_LAO_DONG`: Số người trong độ tuổi lao động (18 đến 60 tuổi).
   * `SO_NGUOI_CO_CCCD`: Số lượng thành viên có CCCD hợp lệ.
   * `PHAN_LOAI_HO`: Nhãn phân loại hộ (lấy giá trị `max`: nếu có thành viên thuộc diện nghèo/cận nghèo thì hộ được gắn nhãn tương ứng).
4. **Kỹ nghệ đặc trưng nâng cao (Advanced Features):**
   * `TY_LE_PHU_THUOC` = `(SO_TRE_EM + SO_NGUOI_GIA) / QUY_MO_HO` (làm tròn 3 chữ số thập phân).
   * `TY_LE_CO_CCCD` = `SO_NGUOI_CO_CCCD / QUY_MO_HO`.
   * `LOAI_HINH_GIA_DINH`: Phân loại hộ theo cấu trúc nhân khẩu học:
     * `Độc thân/Neo đơn`: Hộ chỉ có đúng 1 người.
     * `Đơn thân nuôi con`: Có tối đa 1 lao động và có ít nhất 1 trẻ em.
     * `Người già nương tựa`: Không có trẻ em, không có người trong độ tuổi lao động, chỉ có người cao tuổi (> 60).
     * `Gia đình hạt nhân/Mở rộng`: Có từ 2 người trong độ tuổi lao động trở lên.
     * `Khác`: Các cấu trúc còn lại.
   * `TY_LE_NGHEO_CUA_XA` (**Target Encoding**): Tính tỷ lệ phần trăm hộ nghèo và cận nghèo tại từng địa bàn xã để mô hình học được đặc trưng không gian - kinh tế vi mô của từng vùng.
5. **Kết quả:** Xuất ra file **`DAK_NONG_ML_DATASET.csv`** gồm **22.698 hộ gia đình** với **15 cột đặc trưng** hoàn chỉnh, không còn bất kỳ ô trống nào, sẵn sàng nạp trực tiếp vào pipeline huấn luyện mô hình.

> **Giải thích chênh lệch số lượng hộ giữa ML Dataset (22.698) và Fact Table (23.387):**
> * Tập dữ liệu ML được tạo từ `DAK_NONG_MASTER_POPULATION.csv` (đã qua thuật toán Entity Resolution toàn cục ở Bước 2, loại bỏ các bản ghi trùng lặp do biến động tách hộ, thoát nghèo hoặc trùng lặp CCCD).
> * Tập dữ liệu Star Schema được tổng hợp từ 8 file huyện ở Bước 3 trước khi khử trùng lặp toàn cục, nhằm phản ánh trọn vẹn số lượng hộ đăng ký hành chính tại từng địa phương.

---

<!-- ## 4. Hướng dẫn Triển khai Cơ sở Dữ liệu (PostgreSQL DDL & Data Load)

Mở **pgAdmin 4** (hoặc công cụ dòng lệnh `psql`), tạo database mới (ví dụ: `daknong_dwh`), mở Query Tool và thực thi script SQL sau:

```sql
-- =================================================================
-- 1. BẢNG CHIỀU ĐỊA LÝ (Dim_Geography)
-- =================================================================
DROP TABLE IF EXISTS Dim_Geography CASCADE;
CREATE TABLE Dim_Geography (
    GEO_ID VARCHAR(10) PRIMARY KEY,
    HUYEN VARCHAR(100) NOT NULL,
    XA VARCHAR(100) NOT NULL
);

-- =================================================================
-- 2. BẢNG CHIỀU NHÂN KHẨU HỌC - DÂN TỘC (Dim_Demographic)
-- =================================================================
DROP TABLE IF EXISTS Dim_Demographic CASCADE;
CREATE TABLE Dim_Demographic (
    DEMO_ID INT PRIMARY KEY,
    DEMO_NAME VARCHAR(100) NOT NULL
);

-- =================================================================
-- 3. BẢNG CHIỀU TRẠNG THÁI HỘ (Dim_Household_Status)
-- =================================================================
DROP TABLE IF EXISTS Dim_Household_Status CASCADE;
CREATE TABLE Dim_Household_Status (
    STATUS_ID INT PRIMARY KEY,
    STATUS_NAME VARCHAR(50) NOT NULL
);

-- =================================================================
-- 4. BẢNG SỰ KIỆN HỘ GIA ĐÌNH (Fact_Household)
-- Lưu ý: Sử dụng SURROGATE_ID làm khóa chính tự tăng để đảm bảo
-- tính toàn vẹn khi dữ liệu thô có thể phát sinh mã hộ trùng lặp.
-- =================================================================
DROP TABLE IF EXISTS Fact_Household CASCADE;
CREATE TABLE Fact_Household (
    SURROGATE_ID SERIAL PRIMARY KEY,
    ID_HO_GLOBAL VARCHAR(50) NOT NULL,
    QUY_MO_HO INT NOT NULL,
    LAO_DONG_CHINH INT NOT NULL,
    PHU_THUOC INT NOT NULL,
    TUOI_CHU_HO INT NOT NULL,
    GIOI_TINH_CHU_HO INT NOT NULL,
    STATUS_ID INT REFERENCES Dim_Household_Status(STATUS_ID),
    DEMO_ID INT REFERENCES Dim_Demographic(DEMO_ID),
    GEO_ID VARCHAR(10) REFERENCES Dim_Geography(GEO_ID)
);

-- =================================================================
-- TỐI ƯU HÓA CHỈ MỤC (INDEXING) CHO CÁC TRUY VẤN BI & REPORTING
-- =================================================================
CREATE INDEX idx_fact_geo ON Fact_Household(GEO_ID);
CREATE INDEX idx_fact_status ON Fact_Household(STATUS_ID);
CREATE INDEX idx_fact_demo ON Fact_Household(DEMO_ID);
CREATE INDEX idx_fact_id_ho ON Fact_Household(ID_HO_GLOBAL);
```

### Quy trình Nạp dữ liệu (Data Ingestion Order)

Cần import dữ liệu theo đúng thứ tự ràng buộc khóa ngoại (Foreign Keys):

1. **Bước 1:** Nạp `Star_Schema_DB_Ready/Dim_Household_Status.csv` vào bảng `Dim_Household_Status`.
2. **Bước 2:** Nạp `Star_Schema_DB_Ready/Dim_Demographic.csv` vào bảng `Dim_Demographic`.
3. **Bước 3:** Nạp `Star_Schema_DB_Ready/Dim_Geography.csv` vào bảng `Dim_Geography`.
4. **Bước 4:** Nạp `Star_Schema_DB_Ready/Fact_Household.csv` vào bảng `Fact_Household` (chỉ định rõ danh sách 9 cột: `ID_HO_GLOBAL, QUY_MO_HO, LAO_DONG_CHINH, PHU_THUOC, TUOI_CHU_HO, GIOI_TINH_CHU_HO, STATUS_ID, DEMO_ID, GEO_ID`).

*Lệnh mẫu bằng lệnh `\copy` trong `psql` (thay thế đường dẫn thư mục tương ứng):*

```sql
\copy Dim_Household_Status(STATUS_ID, STATUS_NAME) FROM 'Star_Schema_DB_Ready/Dim_Household_Status.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy Dim_Demographic(DEMO_ID, DEMO_NAME) FROM 'Star_Schema_DB_Ready/Dim_Demographic.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy Dim_Geography(GEO_ID, HUYEN, XA) FROM 'Star_Schema_DB_Ready/Dim_Geography.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy Fact_Household(ID_HO_GLOBAL, QUY_MO_HO, LAO_DONG_CHINH, PHU_THUOC, TUOI_CHU_HO, GIOI_TINH_CHU_HO, STATUS_ID, DEMO_ID, GEO_ID) FROM 'Star_Schema_DB_Ready/Fact_Household.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8'); -->
```

---

## 5. Bảng Thống kê Tổng hợp Chỉ số Dữ liệu (Summary Metrics)

| Chỉ số / Đối tượng | Số lượng thực tế | Nguồn sinh / File lưu trữ |
| :--- | :--- | :--- |
| **Tổng nhân khẩu thô ban đầu** | 107.398 dòng | 8 file Excel trong `Dữ liệu chuẩn hóa/` |
| **Tổng nhân khẩu sau làm sạch cơ bản** | 107.398 dòng | 8 file `*_CLEANED.xlsx` trong `Cleaned_Data_Master/` |
| **Tổng nhân khẩu sau khử trùng lặp toàn tỉnh** | **101.623** người | `DAK_NONG_MASTER_POPULATION.csv` |
| **Tổng số hộ gia đình đăng ký cấp huyện** | **23.387** hộ | `Household_Data/` & `DAK_NONG_HOUSEHOLDS_MASTER.csv` |
<!-- | **Tổng số bản ghi trong Fact Table** | **23.387** hộ | `Star_Schema_DB_Ready/Fact_Household.csv` |
| **Số lượng địa bàn xã/phường chuẩn hóa** | **143** địa bàn | `Star_Schema_DB_Ready/Dim_Geography.csv` |
| **Số nhóm dân tộc ghi nhận thực tế** | **27** nhóm | `Star_Schema_DB_Ready/Dim_Demographic.csv` |
| **Số lượng trạng thái hộ phân loại** | **3** trạng thái | `Star_Schema_DB_Ready/Dim_Household_Status.csv` | -->
| **Tổng số hộ gia đình trong tập dữ liệu ML** | **22.698** hộ | `DAK_NONG_ML_DATASET.csv` |
| **Số đặc trưng đầu vào cho ML** | **15** features | `DAK_NONG_ML_DATASET.csv` |

---

## 6. Quy trình huấn luyện mô hình

<!-- 1. **Phân hệ BI & Dashboard (Power BI / PostgreSQL):**
   * Kết nối Power BI với PostgreSQL hoặc import trực tiếp 4 file CSV từ `Star_Schema_DB_Ready/`.
   * Thiết lập quan hệ hình sao: `1-Many` (Single Direction) từ `Dim_Geography (GEO_ID)`, `Dim_Household_Status (STATUS_ID)`, `Dim_Demographic (DEMO_ID)` tới `Fact_Household`.
   * Xây dựng các biểu đồ KPI chính:
     * Bản đồ tỷ lệ hộ nghèo/cận nghèo theo Huyện và Xã.
     * Cây phân rã nguyên nhân (Decomposition Tree) kết hợp quy mô hộ, số lao động chính và số người phụ thuộc.
     * Phân bố nghèo đói theo độ tuổi và nhóm dân tộc của chủ hộ. -->
2. **Phân hệ Khoa học Dữ liệu & AI (Machine Learning):**
   * Sử dụng tập dữ liệu `DAK_NONG_ML_DATASET.csv`.
   * Chia tập dữ liệu Train/Test theo phân tầng (Stratified K-Fold) dựa trên nhãn mục tiêu `PHAN_LOAI_HO`.
   * Thử nghiệm mô hình phân loại:XGBoost Classifier.
   * Đánh giá độ tin cậy bằng các độ đo: F1-macro, Balanced Accuracy, ROC-AUC (do dữ liệu có sự mất cân bằng giữa hộ nghèo, cận nghèo và hộ thường).
   * Ứng dụng **SHAP (SHapley Additive exPlanations)** để giải thích độ quan trọng của các đặc trưng (Feature Importance), qua đó làm rõ những yếu tố then chốt (như tỷ lệ phụ thuộc, loại hình gia đình, tỷ lệ nghèo của địa bàn xã) tác động đến nguy cơ nghèo đói tại tỉnh Đắk Nông.
