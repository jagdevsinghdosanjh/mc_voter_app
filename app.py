import streamlit as st
from process1 import process1_page
from process2 import process2_page


def main():
    st.set_page_config(page_title="MC Jandiala Guru – Voter Management", layout="wide")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Process",
        ["Process 1 – Old Ward Tagging", "Process 2 – Apply BLO Objections"],
    )

    if page.startswith("Process 1"):
        process1_page()
    else:
        process2_page()


if __name__ == "__main__":
    main()
