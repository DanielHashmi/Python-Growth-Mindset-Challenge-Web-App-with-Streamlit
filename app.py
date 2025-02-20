import os
from io import BytesIO
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Welcome! I'm Daniel Hashmi!", layout='wide')
st.title("Daniel Hashmi")
st.write("Hi there! I'm Daniel Hashmi, a GIAIC student.")

if "original_dataframes" not in st.session_state:
    st.session_state["original_dataframes"] = {}

uploaded_files = st.file_uploader("Upload your CSV or Excel file to get started!", type=[
                                  "csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"File type not supported: {file_ext}")
                continue
        except Exception as e:
            st.error(f"Error processing file {file.name}: {e}")
            continue

        if file.name not in st.session_state["original_dataframes"]:
            st.session_state["original_dataframes"][file.name] = df.copy()
        mutableDF = st.session_state["original_dataframes"][file.name]

        file_size_kb = len(file.getbuffer()) / 1024
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file_size_kb:.2f} KB")
        st.write("### Preview of Uploaded Data")
        st.dataframe(df.head())

        st.subheader("Data Cleaning")
        if st.checkbox(f"Apply cleaning options to {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicate Entries from {file.name}", key=f"remove_duplicates_{file.name}"):
                    mutableDF.drop_duplicates(
                        inplace=True)
                    st.success("Duplicate entries removed.")
                    st.dataframe(
                        mutableDF.head())

            with col2:
                if st.button(f"Fill Missing Values in {file.name}", key=f"fill_missing_{file.name}"):
                    numeric_cols = mutableDF.select_dtypes(
                        include=['number']).columns
                    if len(numeric_cols) > 0:
                        mutableDF[numeric_cols] = mutableDF[numeric_cols].fillna(
                            mutableDF[numeric_cols].mean())
                        st.success(
                            "Missing values filled with column averages.")
                        st.dataframe(
                            mutableDF.head())
                    else:
                        st.warning(
                            "No numeric columns available to fill missing values.")

        st.subheader("Select Columns for Chart Generation")
        chart_columns = st.multiselect(
            f"Select columns to include in the chart for {file.name}",
            options=df.columns.tolist(
            ),
            default=mutableDF.columns.tolist(
            )
        )
        st.subheader("Visualize Your Data")
        if st.checkbox(f"Generate Visualization for {file.name}", key=f"visualize_{file.name}"):
            if chart_columns:
                chart_df = df[chart_columns]
                numeric_chart_df = chart_df.select_dtypes(include='number')
                if numeric_chart_df.empty:
                    st.warning(
                        "No numeric columns available in the selected data for visualization.")
                else:
                    st.bar_chart(numeric_chart_df)
            else:
                st.error("Please select at least one column for charting.")

        st.subheader("Convert & Download")
        conversion_type = st.radio(f"Choose a format to convert {file.name}:", [
                                   "CSV", "Excel"], key=f"conversion_{file.name}")

        buffer = BytesIO()
        if conversion_type == "CSV":
            mutableDF[chart_columns].to_csv(
                buffer, index=False)
            file_name = file.name.replace(file_ext, ".csv")
            mime_type = "text/csv"
        else:  # Excel
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                mutableDF[chart_columns].to_excel(
                    writer, index=False)
            file_name = file.name.replace(file_ext, ".xlsx")
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        buffer.seek(0)  # Reset buffer
        st.download_button(
            label=f"Download {file.name} as {conversion_type}",
            data=buffer,
            file_name=file_name,
            mime=mime_type
        )

st.success("All files have been successfully processed!")
