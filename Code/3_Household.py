import pandas as pd

INPUT_FILE = "../DAK_NONG_MASTER_POPULATION_CLEAN.xlsx"
EXCEL_OUTPUT_FILE = "../DAK_NONG_HOUSEHOLD.xlsx"
CSV_OUTPUT_FILE = "../DAK_NONG_HOUSEHOLD.csv"

MALE = 1
FEMALE = 2
HOUSEHOLD_HEAD = 1


def read_data():
    df = pd.read_excel(INPUT_FILE)

    required_columns = [
        "ID_HO_GLOBAL",
        "QUANHE_CHUHO",
        "GIOI_TINH",
        "TUOI",
        "HUYEN",
        "XA",
        "PHAN_LOAI_HO",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Thiếu các cột bắt buộc: {missing_columns}")

    return df


def normalize_data(df):
    df = df.copy()

    df["ID_HO_GLOBAL"] = df["ID_HO_GLOBAL"].astype("string").str.strip()

    df["TUOI"] = pd.to_numeric(df["TUOI"], errors="coerce")
    df["GIOI_TINH"] = pd.to_numeric(df["GIOI_TINH"], errors="coerce")
    df["QUANHE_CHUHO"] = pd.to_numeric(df["QUANHE_CHUHO"], errors="coerce")
    df["PHAN_LOAI_HO"] = pd.to_numeric(df["PHAN_LOAI_HO"], errors="coerce")

    if df["ID_HO_GLOBAL"].isna().any() or (df["ID_HO_GLOBAL"] == "").any():
        raise ValueError("Phát hiện ID_HO_GLOBAL bị thiếu.")

    if df[["GIOI_TINH", "QUANHE_CHUHO"]].isna().any().any():
        raise ValueError(
            "Phát hiện dữ liệu thiếu hoặc không hợp lệ trong "
            "GIOI_TINH hoặc QUANHE_CHUHO."
        )

    return df


def engineer_member_features(df):
    df = df.copy()

    age = df["TUOI"]
    gender = df["GIOI_TINH"]

    male = gender == MALE
    female = gender == FEMALE
    unknown_gender = ~gender.isin([MALE, FEMALE])

    df["NAM_LAO_DONG"] = (male & age.between(15, 62)).astype(int)

    df["NU_LAO_DONG"] = (female & age.between(15, 60)).astype(int)

    df["TRE_EM"] = (age < 15).astype(int)

    df["NGUOI_GIA"] = (
        (male & (age > 62)) | (female & (age > 60)) | (unknown_gender & (age > 60))
    ).astype(int)

    return df


def aggregate_household_features(df):
    household_df = df.groupby("ID_HO_GLOBAL", as_index=False).agg(
        HUYEN=("HUYEN", "first"),
        XA=("XA", "first"),
        QUY_MO_HO=("ID_HO_GLOBAL", "size"),
        SO_NAM_LAO_DONG=("NAM_LAO_DONG", "sum"),
        SO_NU_LAO_DONG=("NU_LAO_DONG", "sum"),
        SO_TRE_EM=("TRE_EM", "sum"),
        SO_NGUOI_GIA=("NGUOI_GIA", "sum"),
    )

    return household_df


def extract_household_head(df):
    head_df = df[df["QUANHE_CHUHO"] == HOUSEHOLD_HEAD][
        ["ID_HO_GLOBAL", "GIOI_TINH", "TUOI", "PHAN_LOAI_HO"]
    ].copy()

    duplicate_heads = head_df[head_df.duplicated(subset=["ID_HO_GLOBAL"], keep=False)]

    if not duplicate_heads.empty:
        print(
            f"Cảnh báo: Có {duplicate_heads['ID_HO_GLOBAL'].nunique()} hộ "
            "có nhiều hơn một chủ hộ."
        )

    head_df = head_df.drop_duplicates(subset=["ID_HO_GLOBAL"], keep="first")

    head_df = head_df.rename(
        columns={
            "GIOI_TINH": "GIOI_TINH_CHU_HO",
            "TUOI": "TUOI_CHU_HO",
        }
    )

    return head_df


def build_household_dataset(df):
    df = normalize_data(df)

    df = engineer_member_features(df)

    household_df = aggregate_household_features(df)

    head_df = extract_household_head(df)

    household_df = household_df.merge(
        head_df,
        on="ID_HO_GLOBAL",
        how="left",
        validate="one_to_one",
    )

    output_columns = [
        "ID_HO_GLOBAL",
        "HUYEN",
        "XA",
        "QUY_MO_HO",
        "SO_NAM_LAO_DONG",
        "SO_NU_LAO_DONG",
        "SO_TRE_EM",
        "SO_NGUOI_GIA",
        "GIOI_TINH_CHU_HO",
        "TUOI_CHU_HO",
        "PHAN_LOAI_HO",
    ]

    household_df = household_df[output_columns].copy()

    integer_columns = [
        "QUY_MO_HO",
        "SO_NAM_LAO_DONG",
        "SO_NU_LAO_DONG",
        "SO_TRE_EM",
        "SO_NGUOI_GIA",
        "GIOI_TINH_CHU_HO",
        "TUOI_CHU_HO",
        "PHAN_LOAI_HO",
    ]

    for col in integer_columns:
        household_df[col] = household_df[col].astype("Int64")

    return household_df


def export_data(df):
    df.to_excel(
        EXCEL_OUTPUT_FILE,
        index=False,
        sheet_name="Household_Features",
    )

    df.to_csv(
        CSV_OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Đã xuất Excel: {EXCEL_OUTPUT_FILE}")
    print(f"Đã xuất CSV: {CSV_OUTPUT_FILE}")


def main():
    try:
        print("Đang đọc dữ liệu...")
        df = read_data()

        print(f"Tổng số thành viên: {len(df):,}")

        print("Đang thực hiện Feature Engineering...")
        household_df = build_household_dataset(df)

        print("Đang xuất dữ liệu...")
        export_data(household_df)

        print(f"Tổng số hộ gia đình: {len(household_df):,}")
        print("Hoàn thành Feature Engineering!")

    except FileNotFoundError:
        print(f"Không tìm thấy file: {INPUT_FILE}")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


if __name__ == "__main__":
    main()
