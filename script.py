from edgar import *
import streamlit as st
import shutil
import json
import os
import zipfile

st.title('SEC Report Downloader')
st.text('Choose the company for which the reports should be downloaded, and then click Retrieve Reports.')

# Initialize session state
if "is_retrieving" not in st.session_state:
    st.session_state.is_retrieving = False

# Load JSON data
with open('titles_ciks.json') as f: 
    json_titles_ciks = json.load(f)
with open('tickers_ciks.json') as f: 
    json_tickers_ciks = json.load(f)

# Form to group inputs and button
with st.form("report_form"):
    # Disable inputs when reports are being retrieved
    select_method = st.selectbox('Select Company by', options=['Ticker', 'Title'], disabled=st.session_state.is_retrieving)

    if select_method == 'Ticker':
        choice = st.selectbox('Select Ticker', options=json_tickers_ciks.keys(), disabled=st.session_state.is_retrieving)
    elif select_method == 'Title':
        choice = st.selectbox('Select Title', options=json_titles_ciks.keys(), disabled=st.session_state.is_retrieving)

    report_type = st.selectbox('Select Report type', options=["10-K"], disabled=st.session_state.is_retrieving)

    # Button to trigger report retrieval
    submit_button = st.form_submit_button(
        "Retrieve Reports",
        disabled=st.session_state.is_retrieving
    )

# Logic to retrieve reports
if submit_button:
    # Disable inputs and button
    st.session_state.is_retrieving = True

    # Prepare temporary directory
    if os.path.exists('temp'):
        shutil.rmtree('temp')
    os.mkdir('temp')

    # Progress bar
    progress_bar = st.progress(0, text='Retrieving Reports')

    # Get the CIK based on the user's selection
    if select_method == 'Ticker': 
        cik = json_tickers_ciks[choice]
    elif select_method == 'Title': 
        cik = json_titles_ciks[choice]

    # Set the EDGAR identity and fetch filings
    set_identity("contact@secrag.com")
    entity = get_entity(cik)
    filings = entity.get_filings().filter(date="1990-01-01:", form=report_type)
    
    # Download filings
    for count, filing in enumerate(filings):
        try:
            file_path = f"temp/{filing.cik}-{filing.filing_date}.txt"
            with open(file_path, "w") as f: 
                f.write(filing.markdown())
        except Exception as e:
            st.write(f"Failed to download {filing.cik}-{filing.filing_date}.txt: {e}")

        # Update progress bar
        progress_bar.progress((count + 1) / len(filings), text=f'Retrieving Reports: {count + 1}/{len(filings)}')
    
    # Zip the downloaded reports
    zip_filename = 'reports.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk('temp'):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
    
    # Provide download button for the ZIP file
    with open(zip_filename, 'rb') as zip_file:
        st.download_button(
            label="Download All Reports as ZIP",
            data=zip_file,
            file_name=zip_filename,
            mime='application/zip',
            type='primary'
        )
    
    # Re-enable inputs and button
    st.session_state.is_retrieving = False
