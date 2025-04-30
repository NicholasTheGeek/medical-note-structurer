import streamlit as st
import pandas as pd
import requests
import json

# Configure page settings for a clean and modern layout
st.set_page_config(
    page_title="Medical Note Structurer",  # Page title in the browser tab
    page_icon="🏥",  # Emoji icon
    layout="centered"  # Centered layout for better UX
)

# Custom CSS for a polished look
st.markdown(
    """
    <style>
    .main {background-color: #f8f9fa;}  /* Set background color */
    .stButton>button {background-color: #4F8BF9; color: white;}  /* Style buttons */
    .stDownloadButton>button {background-color: #4F8BF9; color: white;}  /* Style download button */
    </style>
    """,
    unsafe_allow_html=True
)

# Title and description
st.title("🏥 Medical Note Structurer")
st.caption("Easily extract structured data from your clinical notes.")

# Expander with usage instructions
with st.expander("ℹ️ How to use this app", expanded=False):
    st.markdown(
        """
        1. **Upload** your clinical notes as a CSV file (must include a `doctor_notes` column).
        2. The app will process each note and extract structured information.
        3. **Download** the structured results as a CSV.
        """
    )

# File uploader widget for CSV files
uploaded_file = st.file_uploader(
    "📄 Upload clinical notes CSV",
    type="csv",  # Only allows CSV files
    help="CSV must contain a 'doctor_notes' column."
)

if uploaded_file:
    # Read uploaded CSV file into a DataFrame
    df = pd.read_csv(uploaded_file)

    # Check for required column
    if "doctor_notes" not in df.columns:
        st.error("The uploaded CSV must contain a 'doctor_notes' column.")
    else:
        results = []  # List to store extracted data
        total = len(df)  # Total number of rows in the file
        progress = st.progress(0, text="Starting extraction...")  # Initialize progress bar

        # Spinner for visual feedback during processing
        with st.spinner("🔎 Extracting info from notes..."):
            for idx, row in df.iterrows():
                try:
                    # Send POST request to the backend API
                    response = requests.post(
                        "http://localhost:8000/extract/",  # Backend API endpoint
                        json={"note": row["doctor_notes"]}  # Pass the note as JSON
                    )
                    response.raise_for_status()  # Raise error for bad responses (4xx/5xx)

                    # Parse the JSON response
                    structured = response.json()
                except Exception as e:
                    # Default values if API request fails
                    structured = {"symptoms": "N/A", "diagnosis": "N/A", "medication": "N/A", "follow_up": "N/A"}

                # Append results with patient ID and structured data
                results.append({
                    "patient_id": row.get("patient_id", f"unknown_{idx}"),  # Use provided ID or fallback
                    "symptoms": structured.get("symptoms", "N/A"),
                    "diagnosis": structured.get("diagnosis", "N/A"),
                    "medication": structured.get("medication", "N/A"),
                    "follow_up": structured.get("follow_up", "N/A")
                })

                # Update progress bar
                progress.progress((idx + 1) / total, text=f"Processing note {idx + 1} of {total}")

        # Convert the results to a DataFrame
        result_df = pd.DataFrame(results)

        # Normalize DataFrame for display
        for column in result_df.columns:
            result_df[column] = result_df[column].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))

        # Handle missing values
        result_df.fillna("N/A", inplace=True)

        # Display success message and results
        st.success("✅ Extraction complete!")

        # Expander to view structured data
        with st.expander("🔬 View Structured Data", expanded=True):
            st.dataframe(result_df, use_container_width=True)

        # Download button for the extracted results
        st.download_button(
            label="⬇️ Download Structured Notes",
            data=result_df.to_csv(index=False),  # Convert DataFrame to CSV
            file_name="structured_notes.csv",  # Default file name
            mime="text/csv"  # MIME type
        )
else:
    # Show information if no file is uploaded
    st.info("Please upload a CSV file to get started.")