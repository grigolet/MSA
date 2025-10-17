import streamlit as st
import pandas as pd
import tempfile
import subprocess
from pathlib import Path
import cleantext
import easyocr

# Configure Streamlit page
st.set_page_config(
    page_title="Metal Slug Awakening - OCR Player Power Analysis",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Metal Slug Awakening - Player Power OCR")
st.markdown("Upload screenshots from the game to extract player names and power levels using OCR.")

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'suspects_data' not in st.session_state:
    st.session_state.suspects_data = None

def crop_images(temp_dir, uploaded_files):
    """Crop uploaded images using the crop.sh script logic"""
    cropped_dir = Path(temp_dir) / "cropped"
    cropped_dir.mkdir(exist_ok=True)
    
    cropped_files = []
    
    for uploaded_file in uploaded_files:
        # Save uploaded file to temp directory
        temp_file_path = Path(temp_dir) / uploaded_file.name
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Crop the image using ImageMagick (equivalent to crop.sh)
        cropped_file_path = cropped_dir / uploaded_file.name
        try:
            # Use ImageMagick to crop: -crop 417x380+447+170
            subprocess.run([
                "magick", str(temp_file_path), 
                "-crop", "417x380+447+170", 
                "+repage", str(cropped_file_path)
            ], check=True, capture_output=True)
            cropped_files.append(str(cropped_file_path))
        except subprocess.CalledProcessError as e:
            st.error(f"Error cropping {uploaded_file.name}: {e}")
            continue
        except FileNotFoundError:
            st.error("ImageMagick (magick command) not found. Please install ImageMagick.")
            return []
    
    return cropped_files

def process_images_with_ocr(cropped_files):
    """Process cropped images with OCR and extract player data"""
    if not cropped_files:
        return pd.DataFrame(), []
    
    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'], gpu=False)
    
    parsed_all = []
    suspects_all = []
    
    # Process each cropped image
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, file_path in enumerate(cropped_files):
        status_text.text(f"Processing image {i+1}/{len(cropped_files)}...")
        progress_bar.progress((i + 1) / len(cropped_files))
        
        try:
            # Run OCR on the image
            results = reader.readtext(file_path, detail=0, paragraph=False)
            
            # Parse OCR results using cleantext module
            parsed, suspects = cleantext.parse_ocr_lines(results)
            
            if not parsed.empty:
                parsed_all.append(parsed)
            
            suspects_all.extend(suspects)
            
        except Exception as e:
            st.error(f"Error processing {file_path}: {e}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    # Combine all parsed data
    if parsed_all:
        df = pd.concat(parsed_all, ignore_index=True)
        # Deduplicate by player name, keeping maximum power
        df = df.groupby("Player Name", as_index=False)["Power"].max()
        df = df.sort_values(by="Power", ascending=False).reset_index(drop=True)
    else:
        df = pd.DataFrame(columns=["Player Name", "Power"])
    
    return df, suspects_all

def main():
    # File uploader
    st.subheader("📁 Upload Screenshots")
    uploaded_files = st.file_uploader(
        "Choose screenshot files (up to 16 images)",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Upload screenshots from Metal Slug Awakening showing player power levels"
    )
    
    if uploaded_files:
        if len(uploaded_files) > 16:
            st.warning("Maximum 16 files allowed. Please select fewer files.")
            return
        
        st.success(f"Uploaded {len(uploaded_files)} file(s)")
        
        # Show uploaded files
        with st.expander("📋 Uploaded Files"):
            for file in uploaded_files:
                st.write(f"- {file.name} ({file.size} bytes)")
        
        # Process button
        if st.button("🔍 Process Images", type="primary"):
            with st.spinner("Processing images..."):
                # Create temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    st.info("Cropping images...")
                    cropped_files = crop_images(temp_dir, uploaded_files)
                    
                    if cropped_files:
                        st.info("Running OCR analysis...")
                        df, suspects = process_images_with_ocr(cropped_files)
                        
                        # Store results in session state
                        st.session_state.processed_data = df
                        st.session_state.suspects_data = suspects
                    else:
                        st.error("Failed to crop images. Please check that ImageMagick is installed.")
    
    # Display results if available
    if st.session_state.processed_data is not None:
        df = st.session_state.processed_data
        suspects = st.session_state.suspects_data
        
        st.subheader("📊 Player Power Analysis Results")
        
        if not df.empty:
            # Add malformed flag column
            df_display = df.copy()
            df_display['Malformed'] = False
            
            # Mark suspects as malformed
            suspect_names = set()
            if suspects:
                for name, _, _ in suspects:
                    suspect_names.add(name)
            
            df_display.loc[df_display['Player Name'].isin(suspect_names), 'Malformed'] = True
            
            # Format power values with commas
            df_display['Power'] = df_display['Power'].apply(lambda x: f"{x:,}")
            
            # Display the main table
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Player Name": st.column_config.TextColumn("Player Name", width="medium"),
                    "Power": st.column_config.TextColumn("Power", width="medium"),
                    "Malformed": st.column_config.CheckboxColumn("Suspected Malformed", width="small")
                }
            )
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Players", len(df))
            with col2:
                st.metric("Highest Power", f"{df['Power'].max():,}" if not df.empty else "0")
            with col3:
                st.metric("Suspected Malformed", len(suspects))
            
            # Download CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="players_power.csv",
                mime="text/csv"
            )
            
            # Copy-paste ready format
            with st.expander("📋 Copy-Paste Ready Format"):
                copy_text = "\n".join([f"{row['Player Name']},{row['Power']}" for _, row in df.iterrows()])
                st.code(copy_text, language="text")
        
        else:
            st.warning("No valid player data found in the uploaded images.")
        
        # Show suspects if any
        if suspects:
            with st.expander("⚠️ Suspected Malformed Entries"):
                st.write("These entries were flagged as potentially malformed during processing:")
                suspects_df = pd.DataFrame(suspects, columns=["Player Name", "Raw Power Text", "Reason"])
                st.dataframe(suspects_df, use_container_width=True, hide_index=True)

    # Instructions
    with st.sidebar:
        st.header("📖 Instructions")
        st.markdown("""
        1. **Take Screenshots**: Capture screenshots from Metal Slug Awakening showing the member list with power levels
        
        2. **Upload Images**: Select up to 16 screenshot files (JPG, JPEG, or PNG)
        
        3. **Process**: Click the "Process Images" button to:
           - Crop images to focus on relevant areas
           - Extract text using OCR
           - Clean and parse player names and power levels
        
        4. **Review Results**: Check the processed data table and download results as CSV
        
        **Note**: Make sure ImageMagick is installed for image cropping functionality.
        """)
        
        st.header("🔧 Settings")
        with st.expander("OCR Configuration"):
            st.info("Current settings from cleantext.py:")
            st.code(f"""
MIN_DIGITS = {cleantext.MIN_DIGITS}
STRICT_MIN_POWER = {cleantext.STRICT_MIN_POWER:,} if cleantext.STRICT_MIN_POWER else None
            """)

if __name__ == "__main__":
    main()
