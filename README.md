# Dự án Phân tích Dữ liệu An sinh Xã hội & Dự đoán Nghèo đói tỉnh Đắk Nông

## 1. Tổng quan Dự án (Project Overview)

Dự án này thực hiện quy trình chuẩn hóa, làm sạch dữ liệu hành chính - an sinh xã hội cấp huyện của tỉnh Đắk Nông (dữ liệu từ các cuộc khảo sát, rà soát hộ nghèo và cận nghèo định kỳ), giải quyết thực thể (Entity Resolution), và xây dựng mô hình Trí tuệ Nhân tạo (Machine Learning & Explainable AI) phục vụ dự đoán và phân tích nguy cơ nghèo đói.

### Phân công Nhiệm vụ trong Nhóm:
* **Phần tác giả trực tiếp phụ trách & thực hiện (Nội dung tài liệu này):**
  1. **Tiền xử lý & Cứu dữ liệu vỡ cấu trúc:** Xử lý 8 file dữ liệu thô cấp huyện bị lỗi vật lý nghiêm trọng (trượt cột, lệch dòng, mất số 0 đầu CCCD, sai định dạng ngày sinh).
  2. **Giải quyết Thực thể Toàn cục (Entity Resolution & Deduplication):** Hợp nhất toàn tỉnh, phát hiện CCCD rác, khử trùng lặp nhân khẩu, chuẩn hóa tên và sắp xếp tự nhiên theo hộ gia đình.
  3. **Kỹ nghệ Đặc trưng Cấp Hộ cho AI (ML Feature Engineering):** Gom nhóm nhân khẩu thành cấp hộ gia đình, trích xuất đặc trưng chủ hộ, phân loại cấu trúc hộ, tính toán tỷ lệ phụ thuộc và tỷ lệ có CCCD.
  4. **Huấn luyện Mô hình Machine Learning & Phân tích Đóng góp (XAI):** Xây dựng pipeline hoàn chỉnh trên notebook với mô hình **XGBoost Classifier**, áp dụng Smoothed Target Encoding theo cấp xã, tối ưu hóa siêu tham số chống Overfitting, đánh giá hiệu năng và bóc tách các nguyên nhân cốt lõi gây nghèo bằng **SHAP (SHapley Additive exPlanations)**.
* **Phần thành viên khác phụ trách (Sẽ tự cập nhật vào README sau):**
  * Mô hình hóa dữ liệu và xây dựng hệ thống Báo cáo trực quan hóa (Dashboard) **thực hiện trực tiếp trên Power BI** (không qua trung gian cơ sở dữ liệu PostgreSQL).
  * *(Lưu ý: Các file và thư mục tạm thời liên quan đến Star Schema trước đây như `Star_Schema_DB_Ready/` hay `Household_Data/` là các phiên bản thử nghiệm cũ, hiện tại luồng Power BI được thành viên phụ trách xây dựng trực tiếp trên Power BI).*

---

## 2. Cấu trúc Thư mục Thực tế (Project Directory Structure)

Cấu trúc tập trung vào các thư mục và tập tin do tác giả trực tiếp phát triển:

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
├── Code/                                    # Kịch bản Python xử lý dữ liệu và giải quyết thực thể
│   ├── 1_Dak_Mil.py                         # Thuật toán AI bóc tách và dọn rác cấu trúc vỡ nát đặc thù cho Đắk Mil
│   ├── 1_Krong_No.py                        # Thuật toán nắn cột trôi Xã sang Tỉnh và lệch Ngày sinh cho Krông Nô
│   ├── 1_PreprocessingMaster.py             # Pipeline tiền xử lý vạn năng chạy chuẩn hóa cho 6 huyện/TP còn lại
│   └── 2_MergeAndDeduplicate.py             # Hợp nhất 8 file sạch, xử lý số 0 CCCD, khử trùng lặp thực thể toàn tỉnh
│
├── Code ML/                                 # Kịch bản Python & Notebook phân tích, mô hình hóa Machine Learning
│   ├── Generate_ML_Dataset.py               # Feature Engineering từ Master Population sang Dataset cấp Hộ cho ML
│   └── Dak_Nong.ipynb                       # Notebook hoàn chỉnh: Huấn luyện XGBoost, Target Encoding & SHAP Analysis
│
├── DAK_NONG_MASTER_POPULATION.csv           # File Tổng 101.623 nhân khẩu toàn tỉnh đã sạch & khử trùng (Kết quả Bước 2)
└── DAK_NONG_ML_DATASET.csv                  # File Dataset 22.698 hộ sạch 100% kèm 15 đặc trưng cho ML (Kết quả Bước 3)
```

---

## 3. Quy trình Thực thi Chi tiết (Pipeline Execution Workflow)

Toàn bộ quy trình do tác giả xây dựng được vận hành theo luồng tuần tự khép kín:

```
[Dữ liệu thô Excel (8 huyện)]
        │
        ▼ (Bước 1: 1_Dak_Mil.py, 1_Krong_No.py, 1_PreprocessingMaster.py)
[Cleaned_Data_Master/*_CLEANED.xlsx] (107.398 nhân khẩu đã nắn chuẩn)
        │
        ▼ (Bước 2: 2_MergeAndDeduplicate.py)
[DAK_NONG_MASTER_POPULATION.csv] (101.623 nhân khẩu sau Entity Resolution toàn tỉnh)
        │
        ▼ (Bước 3: Code ML/Generate_ML_Dataset.py)
[DAK_NONG_ML_DATASET.csv] (22.698 hộ gia đình, 15 đặc trưng hoàn chỉnh)
        │
        ▼ (Bước 4: Code ML/Dak_Nong.ipynb)
[Mô hình XGBoost Classifier + Dashboard Trực quan + Báo cáo SHAP Insight]
```

---

### Bước 1: Tiền xử lý & Nắn cột cấp cơ sở (Tiền tố `1_`)

Dữ liệu thô từ các huyện gặp nhiều dị tật kỹ thuật do quá trình nhập liệu thủ công: ô bị xóa ngẫu nhiên làm xô lệch các cột liền kề, ngày sinh lẫn vào cột quan hệ chủ hộ, CCCD bị Excel đổi thành dạng số khoa học (`6.71E+10`), số 0 đầu chuỗi bị cắt mất.

* **`Code/1_Dak_Mil.py`**:
  * Đọc sheet dữ liệu `DM 31-8-2023` (bỏ qua sheet rỗng `foxz`).
  * Sử dụng thuật toán bóc tách thông minh dựa trên biểu thức chính quy (`ai_rescue_broken_row`) để duyệt từng dòng lỗi (dòng thiếu Tỉnh hoặc Tỉnh không phải Đắk Nông):
    * Tự động quét và nhặt tên Xã (dựa trên các tiền tố `ĐẮK`, `DAK`, `ĐĂK`).
    * Nhận diện Ngày sinh (chuỗi chứa năm `19xx`/`20xx`, tự sửa lỗi gõ 2 dấu gạch chéo `//`, hoặc chuyển đổi ngày dạng số nguyên Serial của Excel từ 10.000 đến 50.000 về ngày chuẩn).
    * Bóc tách số CCCD/Định danh (chuỗi 8-12 chữ số, giải mã chuỗi `E+10`/`E+09`).
    * Nhận diện họ tên Chủ hộ và Thành viên (chuỗi chữ dài hơn 4 ký tự không chứa số).
    * Nhận diện giới tính (số 1 hoặc 2 đứng đơn lẻ).
    * Tái cấu trúc lại dòng và suy luận quan hệ chủ hộ (nếu tên thành viên trùng tên chủ hộ thì gán mã `1`, khác thì gán mã `3`).
  * Chuẩn hóa mã dân tộc (34 dân tộc theo từ điển tra cứu chuẩn), lọc bỏ các dòng ghi chú người đã mất (`chết`, `mất`, `qua đời`, `từ trần`).
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

### Bước 3: Feature Engineering cho Machine Learning (`Code ML/Generate_ML_Dataset.py`)

Kịch bản chuyển đổi dữ liệu từ cấp nhân khẩu sang cấp hộ gia đình độc lập cho bài toán dự đoán nghèo đói. Kịch bản này đọc trực tiếp từ **`DAK_NONG_MASTER_POPULATION.csv`** (tập dữ liệu nhân khẩu đã khử trùng lặp toàn diện ở Bước 2):

1. **Early Imputation (Điền khuyết sớm):**
   * Trám Huyện từ tiền tố ID, Xã trống gán `"CHƯA RÕ"`.
   * Phân loại hộ trống điền `0` (Hộ bình thường / đã thoát nghèo).
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
   * `TY_LE_NGHEO_CUA_XA` (**Target Encoding**): Tính tỷ lệ phần trăm hộ nghèo và cận nghèo tại từng địa bàn xã để phản ánh đặc trưng không gian - kinh tế vi mô của từng vùng.
5. **Kết quả:** Xuất ra file **`DAK_NONG_ML_DATASET.csv`** gồm **22.698 hộ gia đình** với **15 cột đặc trưng** hoàn chỉnh, không còn bất kỳ ô trống nào.

---

### Bước 4: Huấn luyện Mô hình Machine Learning & Phân tích Đóng góp SHAP (`Code ML/Dak_Nong.ipynb`)

Notebook hoàn chỉnh gồm **13 cells** chuyên nghiệp, áp dụng mô hình **XGBoost Classifier** kết hợp giải thích mô hình bằng **SHAP**:

#### 1. Các cải tiến kỹ thuật nổi bật trong Notebook:
* **Đường dẫn linh hoạt:** Tự động tìm kiếm file dữ liệu tại thư mục hiện tại, thư mục cha hoặc môi trường Kaggle/Colab.
* **Tích hợp lệnh cài đặt thư viện tự động (`%pip install -q ...`):** Đảm bảo cài đúng môi trường kernel Python đang chạy.
* **Smoothed Target Encoding chuẩn xác cho cấp Xã:**
  * Thay vì gộp chung {Nghèo, Cận nghèo} khiến tỷ lệ bị bão hòa ở mức 98%, notebook tính toán **tỷ lệ Hộ nghèo thuần túy ($y=1$)** kèm làm mượt $m$-estimate ($m=10$) trên tập Train:
    $$\text{SMOOTHED\_RATE} = \frac{\text{count} \times \text{mean} + m \times \text{global\_mean}}{\text{count} + m}$$
  * Đặc trưng này có độ lệch chuẩn cao ($\sigma = 0.37$), giúp mô hình phân định rõ rệt ranh giới nhạy cảm giữa **Hộ nghèo (Class 1)** và **Hộ cận nghèo (Class 2)**.
* **Bổ sung các đặc trưng kinh tế - xã hội chuyên sâu:**
  * `TY_LE_PHU_THUOC_LAO_DONG`: $(\text{Trẻ em} + \text{Người già}) / (\text{Lao động} + 1)$ phản ánh gánh nặng kinh tế trực tiếp lên mỗi lao động.
  * `TY_LE_LAO_DONG`: $\text{Lao động} / \text{Quy mô hộ}$.
  * `IS_DAN_TOC_THIEU_SO`: Cờ nhận diện đồng bào dân tộc thiểu số (`DANTOC_CHU_HO != 1`).
  * `IS_NU_DON_THAN`: Cờ nhận diện chủ hộ nữ đơn thân nuôi con.
  * `NHOM_TUOI_CHU_HO`: Phân nhóm độ tuổi chủ hộ (`Tre_Duoi30`, `SungSuc_30_50`, `TienHuu_51_65`, `CaoTuoi_Tren65`) và One-Hot Encoding.
* **Làm sạch tên cột cho XGBoost:** Tự động loại bỏ các ký tự `[`, `]`, `<` để tương thích 100% với trình phân tích DMatrix của XGBoost.
* **Kiểm soát Overfitting & Cân bằng trọng số:**
  * `max_depth=5` (giảm từ 8 để chống học vẹt).
  * Hàm phạt $L_1$ (`reg_alpha=0.5`) và $L_2$ (`reg_lambda=1.5`).
  * `compute_sample_weight('balanced', y_train)` tự động cân bằng lớp thiểu số (Class 0: 2.04%).

#### 2. Kết quả Hiệu năng Mô hình (trên 4.540 hộ tập Test):
* **Độ chính xác tổng thể (Accuracy):** **~78%**.
* **Nhóm Bình Thường (Class 0):** F1-score đạt **0.99 - 1.00** (nhận diện chính xác tuyệt đối).
* **Nhóm Hộ Nghèo (Class 1) & Cận Nghèo (Class 2):** F1-score đạt **~0.78**, phân tách rõ nét nhờ tỷ lệ nghèo thuần túy cấp xã và tỷ số phụ thuộc lao động.

#### 3. Phân tích Khả năng Giải thích (Explainable AI - SHAP):
* **SHAP Beeswarm Plot (Class 1 - Hộ nghèo):** Bóc tách các yếu tố đẩy một gia đình vào lõi nghèo.
  * *Tỷ lệ phụ thuộc trên lao động cao* và *quy mô hộ lớn* là hai yếu tố đẩy giá trị SHAP lên cao nhất.
  * *Tỷ lệ nghèo của địa bàn xã* đóng vai trò phân tầng không gian kinh tế.
  * *Chủ hộ nữ đơn thân nuôi con* và *chủ hộ cao tuổi* có rủi ro nghèo cao hơn rõ rệt.
* **SHAP Bar Plot:** Đánh giá mức độ ảnh hưởng trung bình của từng biến trên toàn bộ 3 phân lớp.

---

## 4. Bảng Thống kê Dữ liệu Thực tế (Summary Metrics)

Bảng tổng hợp số liệu thực tế qua các giai đoạn xử lý do tác giả thực hiện:

| Chỉ số / Đối tượng | Số lượng thực tế | Nguồn sinh / File lưu trữ |
| :--- | :--- | :--- |
| **Tổng nhân khẩu thô ban đầu** | 107.398 dòng | 8 file Excel trong `Dữ liệu chuẩn hóa/` |
| **Tổng nhân khẩu sau khi nắn cột cơ sở** | 107.398 dòng | 8 file `*_CLEANED.xlsx` trong `Cleaned_Data_Master/` |
| **Tổng nhân khẩu sau Entity Resolution toàn tỉnh** | **101.623** người | `DAK_NONG_MASTER_POPULATION.csv` |
| **Tổng số hộ gia đình trong tập dữ liệu ML** | **22.698** hộ | `DAK_NONG_ML_DATASET.csv` |
| **Số đặc trưng đầu vào cho Machine Learning** | **15** features | `DAK_NONG_ML_DATASET.csv` |
| **Kích thước tập huấn luyện (Train Set - 80%)** | **18.158** hộ | Huấn luyện mô hình XGBoost trong `Dak_Nong.ipynb` |
| **Kích thước tập kiểm thử (Test Set - 20%)** | **4.540** hộ | Đánh giá ma trận nhầm lẫn & SHAP trong `Dak_Nong.ipynb` |

---

## 5. Khuyến nghị Chính sách An sinh Xã hội từ Kết quả Mô hình

Từ các phát hiện trực quan hóa của SHAP, tác giả đề xuất 3 nhóm giải pháp chính sách trọng tâm:

1. **Chuyển trọng tâm từ hỗ trợ tiền mặt sang hỗ trợ việc làm & giảm gánh nặng lao động:**
   * Tập trung đào tạo nghề và tạo sinh kế bền vững cho các thành viên trong độ tuổi lao động của hộ cận nghèo để ngăn chặn nguy cơ tái nghèo.
   * Xây dựng mạng lưới trường mầm non công lập và điểm sinh hoạt cộng đồng tại xã để giải phóng sức lao động cho các hộ có tỷ lệ phụ thuộc cao.
2. **Đầu tư có trọng điểm theo bản đồ rủi ro cấp Xã:**
   * Tập trung nguồn lực phát triển hạ tầng giao thông và khuyến nông vào các cụm xã có tỷ lệ nghèo cục bộ cao thay vì phân bổ dàn trải.
3. **Chính sách an sinh đặc thù cho phụ nữ đơn thân và đồng bào dân tộc thiểu số:**
   * Thiết lập các gói tín dụng vi mô ưu đãi không cần thế chấp cho chủ hộ nữ đơn thân nuôi con và hỗ trợ kỹ thuật canh tác thích ứng cho đồng bào thiểu số vùng sâu vùng xa.
