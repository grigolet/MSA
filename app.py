import streamlit as st
import pandas as pd
import tempfile
import subprocess
from pathlib import Path
from PIL import Image
import easyocr
from cleantext import parse_ocr_lines

def main():
    st.title("Metal Slug Awakening - OCR Text Cleaning")
    st.markdown("Upload screenshots from the game to extract player names and power levels from the members club.")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose image files (up to 16 images)",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Upload screenshots from the Metal Slug Awakening members club"
    )
    
    if uploaded_files:
        if len(uploaded_files) > 16:
            st.error("Please upload no more than 16 images.")
            return
        
        st.success(f"Uploaded {len(uploaded_files)} image(s)")
        
        # Show uploaded images in a grid
        if st.checkbox("Show uploaded images"):
            cols = st.columns(min(4, len(uploaded_files)))
            for i, uploaded_file in enumerate(uploaded_files):
                with cols[i % 4]:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=uploaded_file.name, use_column_width=True)
        
        if st.button("Process Images", type="primary"):
            process_images(uploaded_files)

def process_images(uploaded_files):
    """Process the uploaded images through cropping and OCR"""
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Step 1: Save uploaded files
        status_text.text("Saving uploaded files...")
        progress_bar.progress(10)
        
        image_paths = []
        for i, uploaded_file in enumerate(uploaded_files):
            # Save with consistent naming for crop script
            file_path = temp_path / f"photo_{i+1}_2025-10-17_11-58-42.jpg"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            image_paths.append(file_path)
        
        # Step 2: Create cropped directory
        cropped_dir = temp_path / "cropped"
        cropped_dir.mkdir(exist_ok=True)
        
        # Step 3: Crop images using ImageMagick
        status_text.text("Cropping images...")
        progress_bar.progress(30)
        
        try:
            # Check if ImageMagick is available
            subprocess.run(["magick", "-version"], capture_output=True, check=True)
            
            # Crop each image
            for image_path in image_paths:
                crop_cmd = [
                    "magick", str(image_path),
                    "-crop", "417x380+447+170", "+repage",
                    str(cropped_dir / image_path.name)
                ]
                subprocess.run(crop_cmd, check=True, cwd=temp_path)
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            st.error(f"Error cropping images: {e}")
            st.info("ImageMagick is required for image cropping. Please install it or use pre-cropped images.")
            return
        
        # Step 4: Initialize OCR
        status_text.text("Initializing OCR...")
        progress_bar.progress(50)
        
        try:
            reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            st.error(f"Error initializing OCR: {e}")
            return
        
        # Step 5: Process each cropped image
        status_text.text("Processing images with OCR...")
        progress_bar.progress(70)
        
        all_parsed = []
        all_suspects = []
        
        cropped_files = list(cropped_dir.glob("*.jpg"))
        
        if not cropped_files:
            st.error("No cropped images found. There may be an issue with the cropping process.")
            return
        
        for i, image_file in enumerate(cropped_files):
            try:
                # Perform OCR
                results = reader.readtext(str(image_file), detail=0, paragraph=False)
                
                # Parse OCR lines
                parsed_df, suspects = parse_ocr_lines(results)
                
                if not parsed_df.empty:
                    all_parsed.append(parsed_df)
                
                all_suspects.extend(suspects)
                
                # Update progress
                progress = 70 + (i + 1) / len(cropped_files) * 20
                progress_bar.progress(int(progress))
                
            except Exception as e:
                st.warning(f"Error processing {image_file.name}: {e}")
                continue
        
        # Step 6: Combine and deduplicate results
        status_text.text("Combining results...")
        progress_bar.progress(95)
        
        if all_parsed:
            # Combine all DataFrames
            combined_df = pd.concat(all_parsed, ignore_index=True)
            
            # Deduplicate by player name, keeping the highest power
            final_df = combined_df.groupby("Player Name", as_index=False)["Power"].max()
            final_df = final_df.sort_values(by="Power", ascending=False).reset_index(drop=True)
            
            # Add suspected malformed column
            suspected_names = {name for name, _, _ in all_suspects}
            final_df["Suspected Malformed"] = final_df["Player Name"].isin(suspected_names)
            
            progress_bar.progress(100)
            status_text.text("Processing complete!")
            
            # Display results
            display_results(final_df, all_suspects)
            
        else:
            st.error("No valid player data could be extracted from the images.")
            progress_bar.progress(100)
            status_text.text("Processing complete - no data found.")

def display_results(df, suspects):
    """Display the results in Streamlit"""
    
    st.header("Results")
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Players", len(df))
    with col2:
        st.metric("Suspected Issues", df["Suspected Malformed"].sum())
    with col3:
        if not df.empty:
            st.metric("Highest Power", f"{df['Power'].max():,}")
    
    # Main results table
    st.subheader("Player Rankings")
    
    # Style the dataframe
    styled_df = df.copy()
    styled_df["Power"] = styled_df["Power"].apply(lambda x: f"{x:,}")
    
    # Color-code suspected malformed entries
    def highlight_suspected(row):
        if row["Suspected Malformed"]:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)
    
    st.dataframe(
        styled_df.style.apply(highlight_suspected, axis=1),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button for CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="metal_slug_players.csv",
        mime="text/csv"
    )
    
    # Copy-paste friendly format
    st.subheader("Copy-Paste Format")
    copy_text = "\n".join([f"{row['Player Name']},{row['Power']}" for _, row in df.iterrows()])
    st.text_area("Player list (Name,Power)", copy_text, height=200)
    
    # Show suspects if any
    if suspects:
        with st.expander("Suspected Issues (click to expand)", expanded=False):
            st.warning("The following entries may have parsing issues:")
            suspects_df = pd.DataFrame(suspects, columns=["Player Name", "Raw Text", "Issue"])
            st.dataframe(suspects_df, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Metal Slug Awakening OCR",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    main()
