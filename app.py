import os
from io import BytesIO
import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Welcome! I'm Daniel Hashmi!", layout='wide')
st.title("Daniel Hashmi")
st.write("Hi there! I'm Daniel Hashmi, a GIAIC student.")

# Initialize session state to store modified data
if "dataframes" not in st.session_state:
    st.session_state["dataframes"] = {}

# File uploader
uploaded_files = st.file_uploader("Upload your CSV or Excel file to get started!", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files is not None:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[1].lower()
        
        # Read file into DataFrame
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

        # Store the original dataframe in session state if not already there
        if file.name not in st.session_state["dataframes"]:
            st.session_state["dataframes"][file.name] = df.copy()

        # Use the stored dataframe (this ensures modifications persist)
        df = st.session_state["dataframes"][file.name]

        # File details
        file_size_kb = len(file.getbuffer()) / 1024
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file_size_kb:.2f} KB")
        st.write("### Preview of Uploaded Data")
        st.dataframe(df.head())
        
        # Data cleaning options
        st.subheader("Data Cleaning")
        if st.checkbox(f"Apply cleaning options to {file.name}"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Remove Duplicate Entries from {file.name}", key=f"remove_duplicates_{file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.session_state["dataframes"][file.name] = df  # Save changes
                    st.success("Duplicate entries removed.")
                    st.dataframe(df.head())

            with col2:
                if st.button(f"Fill Missing Values in {file.name}", key=f"fill_missing_{file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.session_state["dataframes"][file.name] = df  # Save changes
                    st.success("Missing values filled with column averages.")
                    st.dataframe(df.head())

        # Column selection
        st.subheader("Choose Columns to Keep")
        selected_columns = st.multiselect(f"Select columns to retain from {file.name}", df.columns, default=df.columns)
        df = df[selected_columns]
        st.session_state["dataframes"][file.name] = df  # Save selection
        
        # Data visualization
        st.subheader("Visualize Your Data")
        if st.checkbox(f"Generate Visualization for {file.name}", key=f"visualize_{file.name}"):
            st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])
        
        # Conversion options
        st.subheader("Convert & Download")
        conversion_type = st.radio(f"Choose a format to convert {file.name}:", ["CSV", "Excel"], key=f"conversion_{file.name}")
        
        if st.button(f"Download {file.name} as {conversion_type}", key=f"download_{file.name}"):
            buffer = BytesIO()
            
            # Retrieve the latest modified dataframe from session state
            df = st.session_state["dataframes"][file.name]

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            else:  # Excel
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
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
