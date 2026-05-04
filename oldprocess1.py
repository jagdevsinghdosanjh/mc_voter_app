import re
import streamlit as st
import pandas as pd
from parser import parse_part_from_bytes
from utils import df_to_excel_bytes


def infer_part_no_from_name(name: str) -> int | None:
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else None


def process1_page():
    st.header("Process 1 – Build Master & Old Ward Lists")

    uploaded_files = st.file_uploader(
        "Upload Part-wise Voter PDFs (e.g., Part175.pdf, Part176.pdf, ...)",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if not uploaded_files:
        st.info("Upload one or more Part PDFs to begin.")
        return

    if st.button("Extract All Parts"):
        all_parts: list[pd.DataFrame] = []

        for f in uploaded_files:
            part_no = infer_part_no_from_name(f.name) or 0
            file_bytes = f.read()
            df_part = parse_part_from_bytes(file_bytes, part_no=part_no)
            all_parts.append(df_part)

        if not all_parts:
            st.error("No voters extracted. Check PDFs or parser.")
            return

        master = pd.concat(all_parts, ignore_index=True)
        master["old_ward"] = ""

        st.success(f"Extracted {len(master)} voters from {len(uploaded_files)} parts.")
        st.dataframe(master.head(50), use_container_width=True)

        st.subheader("Optional: Quick Ward Tagging by House No Prefix")
        ward = st.selectbox("Ward to assign", [f"W{i}" for i in range(1, 16)])
        prefix = st.text_input("House No starts with (e.g., '12', '6/A')")

        if st.button("Assign Ward by House No Prefix"):
            mask = master["house_no"].astype(str).str.startswith(prefix, na=False)
            master.loc[mask, "old_ward"] = ward
            st.write(
                f"Assigned {mask.sum()} voters to {ward} based on house_no prefix '{prefix}'."
            )

        st.subheader("Manual Ward Editing")
        edited = st.data_editor(master, num_rows="dynamic", use_container_width=True)

        st.download_button(
            "Download Master with Old Wards",
            data=df_to_excel_bytes(edited),
            file_name="master_old_wards.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        wards = sorted(
            [w for w in edited["old_ward"].unique() if isinstance(w, str) and w.strip()]
        )
        for w in wards:
            ward_df = edited[edited["old_ward"] == w]
            st.download_button(
                f"Download {w} List",
                data=df_to_excel_bytes(ward_df),
                file_name=f"{w}_old.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
