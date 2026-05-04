import streamlit as st
import pandas as pd
from utils import df_to_excel_bytes


def apply_shifts(master_df: pd.DataFrame, shifts_df: pd.DataFrame) -> pd.DataFrame:
    df = master_df.copy()
    df["new_ward"] = df.get("new_ward", df["old_ward"])
    df["shift_flag"] = 0

    merged = df.merge(
        shifts_df[["ac_no", "part_no", "serial_no", "new_ward"]],
        on=["ac_no", "part_no", "serial_no"],
        how="left",
        suffixes=("", "_shift"),
    )

    mask = merged["new_ward_shift"].notna()
    merged.loc[mask, "new_ward"] = merged.loc[mask, "new_ward_shift"]
    merged.loc[mask, "shift_flag"] = 1

    return merged.drop(columns=["new_ward_shift"])


def process2_page():
    st.header("Process 2 – Apply BLO Objections & Build New Ward Lists")

    master_file = st.file_uploader(
        "Upload Master with Old Wards (Excel)", type=["xlsx"]
    )
    shifts_file = st.file_uploader(
        "Upload BLO Objection / Shift File (Excel)", type=["xlsx"]
    )

    if not master_file or not shifts_file:
        st.info("Upload both files to proceed.")
        return

    if st.button("Apply Shifts"):
        master_df = pd.read_excel(master_file)
        shifts_df = pd.read_excel(shifts_file)

        updated = apply_shifts(master_df, shifts_df)

        st.success("Shifts applied successfully.")
        st.dataframe(updated.head(50), width="stretch")

        st.download_button(
            "Download Master with New Wards",
            data=df_to_excel_bytes(updated),
            file_name="master_new_wards.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        wards = sorted(
            [
                w
                for w in updated["new_ward"].dropna().unique()
                if isinstance(w, str) and w.strip()
            ]
        )
        for w in wards:
            ward_df = updated[updated["new_ward"] == w]
            st.download_button(
                f"Download {w} List (New)",
                data=df_to_excel_bytes(ward_df),
                file_name=f"{w}_new.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        shifted = updated[updated["shift_flag"] == 1]
        if not shifted.empty:
            st.download_button(
                "Download Shifted Voters Only",
                data=df_to_excel_bytes(shifted),
                file_name="shifted_voters.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


# import streamlit as st
# import pandas as pd
# from utils import df_to_excel_bytes

# def apply_shifts(master_df: pd.DataFrame, shifts_df: pd.DataFrame) -> pd.DataFrame:
#     df = master_df.copy()
#     if "new_ward" not in df.columns:
#         df["new_ward"] = df.get("old_ward", "")
#     df["shift_flag"] = 0

#     needed_cols = ["ac_no", "part_no", "serial_no", "new_ward"]
#     for col in needed_cols:
#         if col not in shifts_df.columns:
#             raise ValueError(f"Shift file missing column: {col}")

#     merged = df.merge(
#         shifts_df[needed_cols],
#         on=["ac_no", "part_no", "serial_no"],
#         how="left",
#         suffixes=("", "_shift")
#     )

#     mask = merged["new_ward_shift"].notna()
#     merged.loc[mask, "new_ward"] = merged.loc[mask, "new_ward_shift"]
#     merged.loc[mask, "shift_flag"] = 1

#     merged = merged.drop(columns=["new_ward_shift"])
#     return merged

# def process2_page():
#     st.header("Process 2 – Apply BLO Objections & Build New Ward Lists")

#     master_file = st.file_uploader("Upload Master with Old Wards (Excel)", type=["xlsx"], key="master_file")
#     shifts_file = st.file_uploader("Upload BLO Objection / Shift File (Excel)", type=["xlsx"], key="shifts_file")

#     if not master_file or not shifts_file:
#         st.info("Upload both the master file and the shift file to proceed.")
#         return

#     if st.button("Apply Shifts"):
#         master_df = pd.read_excel(master_file)
#         shifts_df = pd.read_excel(shifts_file)

#         try:
#             updated = apply_shifts(master_df, shifts_df)
#         except Exception as e:
#             st.error(f"Error applying shifts: {e}")
#             return

#         st.success("Shifts applied successfully.")
#         st.dataframe(updated.head(50), use_container_width=True)

#         st.download_button(
#             "Download Master with New Wards",
#             data=df_to_excel_bytes(updated),
#             file_name="master_new_wards.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#         wards = sorted([w for w in updated["new_ward"].dropna().unique() if isinstance(w, str) and w.strip()])
#         for w in wards:
#             ward_df = updated[updated["new_ward"] == w]
#             st.download_button(
#                 f"Download {w} List (New)",
#                 data=df_to_excel_bytes(ward_df),
#                 file_name=f"{w}_new.xlsx",
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )

#         shifted = updated[updated["shift_flag"] == 1]
#         if not shifted.empty:
#             st.download_button(
#                 "Download Only Shifted Voters",
#                 data=df_to_excel_bytes(shifted),
#                 file_name="shifted_voters.xlsx",
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )
