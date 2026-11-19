import pandas as pd

INPUT_FILE = "DAK_NONG_MASTER_POPULATION.csv"
CSV_OUTPUT_FILE = "DAK_NONG_MASTER_POPULATION_CLEAN.csv"
EXCEL_OUTPUT_FILE = "DAK_NONG_MASTER_POPULATION_CLEAN.xlsx"

VALID_GENDER = {"1", "2"}
VALID_RELATIONSHIP = {"1", "2", "3", "4", "5"}


def read_data():
    try:
        return pd.read_csv(INPUT_FILE, dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(INPUT_FILE, dtype=str, encoding="utf-8-sig")


def clean_data(df):
    df = df.copy()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)

    integer_columns = [
        "NGAY",
        "THANG",
        "NAM_SINH",
        "TUOI",
        "GIOI_TINH",
        "DANTOC",
        "PHAN_LOAI_HO",
    ]

    for col in integer_columns:
        values = (
            df[col]
            .astype("string")
            .str.strip()
            .str.replace(r"\.0+$", "", regex=True)
            .replace("", pd.NA)
        )

        df[col] = pd.to_numeric(values, errors="coerce").astype("Int64")

    df["PHAN_LOAI_HO"] = df["PHAN_LOAI_HO"].fillna(0).astype("Int64")
    df.loc[~df["TUOI"].between(0, 120), "TUOI"] = pd.NA

    df["SO_CCCD_CLEAN"] = (
        df["SO_CCCD_CLEAN"].astype("string").str.strip().replace("", pd.NA)
    )

    valid_cccd = df["SO_CCCD_CLEAN"].str.fullmatch(r"\d{12}", na=False)

    df["HAS_VALID_CCCD"] = valid_cccd.astype(int).astype(str)

    return df


def remove_empty_records(df):
    empty_records = (
        df["SO_CCCD_CLEAN"].isna() & df["NAM_SINH"].isna() & df["TUOI"].isna()
    )

    removed = empty_records.sum()

    df = df.loc[~empty_records].copy()

    print("\n===== EMPTY RECORD REMOVAL =====")
    print(f"Số bản ghi bị xóa: {removed:,}")
    print(f"Số bản ghi còn lại: {len(df):,}")

    return df


def fill_missing_gender(df):
    missing = df["GIOI_TINH"].isna().sum()

    df["GIOI_TINH"] = df["GIOI_TINH"].fillna(0).astype("Int64")

    print("\n===== GENDER CLEANING =====")
    print(f"Số giới tính bị thiếu: {missing:,}")
    print(f"Số dòng được gán mã 0: {missing:,}")

    return df


def fill_missing_relationship(df):
    df["QUANHE_CHUHO"] = (
        df["QUANHE_CHUHO"]
        .astype("string")
        .str.replace("\u00a0", " ", regex=False)
        .str.strip()
        .str.replace(r"\.0+$", "", regex=True)
        .replace("", pd.NA)
    )

    missing = df["QUANHE_CHUHO"].isna().sum()

    invalid = (
        df["QUANHE_CHUHO"].notna() & ~df["QUANHE_CHUHO"].isin(VALID_RELATIONSHIP)
    ).sum()

    df["QUANHE_CHUHO"] = df["QUANHE_CHUHO"].where(
        df["QUANHE_CHUHO"].isin(VALID_RELATIONSHIP), "0"
    )

    print("\n===== RELATIONSHIP CLEANING =====")
    print(f"Quan hệ chủ hộ bị thiếu: {missing:,}")
    print(f"Quan hệ chủ hộ không hợp lệ: {invalid:,}")
    print(f"Tổng số dòng được gán mã 0: {missing + invalid:,}")

    return df


def fill_missing_ethnicity(df):
    missing = df["DANTOC"].isna().sum()

    df["DANTOC"] = df["DANTOC"].fillna(56).astype("Int64")

    print("\n===== ETHNICITY CLEANING =====")
    print(f"Số dân tộc bị thiếu: {missing:,}")
    print(f"Số dòng được gán mã 56: {missing:,}")

    return df


def fill_missing_commune(df):
    missing = df["XA"].isna().sum()

    df["XA"] = df["XA"].fillna("KHONG_XAC_DINH")

    print("\n===== COMMUNE CLEANING =====")
    print(f"Số xã bị thiếu: {missing:,}")
    print(f"Số dòng được gán KHONG_XAC_DINH: {missing:,}")

    return df


def validate_data(df):
    age = pd.to_numeric(df["TUOI"], errors="coerce")
    cccd = df["SO_CCCD_CLEAN"].astype("string")

    valid_cccd = cccd.str.fullmatch(r"\d{12}", na=False)

    checks = {
        "Tổng số bản ghi": len(df),
        "ID hộ bị thiếu": df["ID_HO_GLOBAL"].isna().sum(),
        "Giới tính không hợp lệ": (~df["GIOI_TINH"].isin({0, 1, 2})).sum(),
        "Quan hệ chủ hộ không hợp lệ": (
            ~df["QUANHE_CHUHO"].isin({"0", *VALID_RELATIONSHIP})
        ).sum(),
        "Tuổi thiếu hoặc không hợp lệ": (~age.between(0, 120)).sum(),
        "Dân tộc bị thiếu": df["DANTOC"].isna().sum(),
        "Xã bị thiếu": df["XA"].isna().sum(),
        "CCCD bị thiếu": cccd.isna().sum(),
        "CCCD đúng 12 chữ số": valid_cccd.sum(),
        "CCCD sai định dạng": (cccd.notna() & ~valid_cccd).sum(),
        "Dòng thuộc nhóm CCCD trùng": (
            cccd.duplicated(keep=False).where(cccd.notna(), False).sum()
        ),
    }

    print("\n===== DATA VALIDATION =====")

    for label, value in checks.items():
        print(f"{label}: {value:,}")


def export_data(df):
    df.to_csv(CSV_OUTPUT_FILE, index=False, encoding="utf-8-sig")

    df.to_excel(
        EXCEL_OUTPUT_FILE, index=False, sheet_name="Population", engine="openpyxl"
    )

    print("\n===== EXPORT COMPLETED =====")
    print(f"CSV: {CSV_OUTPUT_FILE}")
    print(f"Excel: {EXCEL_OUTPUT_FILE}")


def main():
    print("ĐANG ĐỌC DỮ LIỆU...")

    df = read_data()

    print("\nĐANG LÀM SẠCH DỮ LIỆU...")
    df = clean_data(df)
    df = remove_empty_records(df)
    df = fill_missing_gender(df)
    df = fill_missing_relationship(df)
    df = fill_missing_ethnicity(df)
    df = fill_missing_commune(df)

    validate_data(df)

    export_data(df)

    print(f"\nTỔNG SỐ BẢN GHI: {len(df):,}")
    print("HOÀN TẤT!")


if __name__ == "__main__":
    main()
