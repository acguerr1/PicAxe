# main.py
import os
import sys
import time
import shutil
import argparse
import tempfile
import subprocess

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.append(src_path)

# Import the scripts_dir from the config file
from config import config
scripts_dir = config.scripts_dir
sample_papers_dir = config.sample_papers_dir
bulk_papers_dir = config.bulk_papers_dir
pdf_files = config.pdf_files
output_tables_dir = config.output_tables_dir
extracted_images = config.extracted_images

def copy_tables_to_output(output_tables_dir, extracted_images):
    # Ensure the target directory exists
    os.makedirs(extracted_images, exist_ok=True)

    # Copy files from output_tables_dir to extracted_images
    for filename in os.listdir(output_tables_dir):
        src_file = os.path.join(output_tables_dir, filename)
        dest_file = os.path.join(extracted_images, filename)
        
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dest_file)  # Copy the file to the target directory
    return None

# Function to run an individual script
def run_script(script_name):
    try:
        script_path = os.path.join(scripts_dir, script_name)
        
        # Ensure the script has the .py extension
        if not script_path.endswith('.py'):
            script_path += '.py'
        
        # Run the script
        subprocess.run([sys.executable, script_path], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        sys.exit(1)  # Exit if the script fails

def cleanup_after_processing():
    """Clean up logs and intermediate directories after successful processing."""
    import glob
    
    # Clean up logs
    log_files = glob.glob(os.path.join(config.log_dir, "*.json"))
    for log_file in log_files:
        os.remove(log_file)
    
    # Clean up intermediate directories, keep only extracted_images
    intermediate_dirs = [
        config.pages_no_tables_dir, config.pdf_imgs_dir,
        config.bounding_boxes_dir, config.text_removed_dir, config.masking_imgs_dir,
        config.target_images, config.page_output_dir, config.cropped_dir
    ]
    
    for dir_path in intermediate_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    

def main(args):
    temp_dir = None
    try: 
        # Set the location of pdf_files
        if args.input_dir and args.output_dir:
            config.pdf_files = args.input_dir
            # Final outputs go to specified directory
            final_extracted = os.path.join(args.output_dir, 'extracted_images')
            final_tables = os.path.join(args.output_dir, 'tables')
            os.makedirs(final_extracted, exist_ok=True)
            os.makedirs(final_tables, exist_ok=True)
        
        elif args.bulk:
            config.pdf_files = bulk_papers_dir
        elif args.sample:
            config.pdf_files = sample_papers_dir
        elif args.file_name:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
        
            # First try to find the file in sample_papers_dir
            file_path = os.path.join(sample_papers_dir, os.path.basename(args.file_name))
            
            if os.path.exists(file_path):
                # File found in sample_papers_dir
                source_file = file_path
            elif os.path.exists(args.file_name):
                # File found at the provided path
                source_file = args.file_name
            else:
                print(f"Error: The file {args.file_name} does not exist in {sample_papers_dir} or at the provided path.")
                sys.exit(1)
            
            shutil.copy(source_file, temp_dir)
            config.pdf_files = temp_dir

        else:
            
            print("Error: Either --file, --bulk, or --sample, or (--input-dir and --output-dir) must be provided.")
            sys.exit(1)
        
        # Validation of input types
        if not os.path.exists(config.pdf_files) or not os.listdir(config.pdf_files):
            raise ValueError(f"No files found in {config.pdf_files}")
        
        files = os.listdir(config.pdf_files)
        valid_files = [f for f in files if f.endswith(('.pdf'))] # only pdf files
        if not valid_files:
            raise ValueError("No valid image/PDF files found")
        
        # Add the pdf_files to the environment variables so that scripts can access it
        os.environ['PDF_FILES'] = config.pdf_files
       
        start = time.time()  # Record the start time

        # List of scripts to run sequentially
        scripts = ["convert_pdfs_to_images.py", "crop_borders.py", "remove_tables.py", \
                    "remove_text.py", "select_target_images.py", "extract_and_save_images.py"]
        
        # Run each script
        for script in scripts:
            run_script(script)
        
        # Add tables to extracted images
        copy_tables_to_output(output_tables_dir, extracted_images)

        if args.input_dir and args.output_dir:
            # Copy from default locations to specified output
            if os.path.exists(extracted_images):
                shutil.copytree(extracted_images, final_extracted, dirs_exist_ok=True)
                shutil.rmtree(extracted_images)  # Delete original
            if os.path.exists(output_tables_dir):
                shutil.copytree(output_tables_dir, final_tables, dirs_exist_ok=True)
                shutil.rmtree(output_tables_dir)  # Delete original

    except Exception as e:
        print(f"Error encounterd: {str(e)}")
        sys.exit(1)

    finally:
        # Clean up the temporary directory if it was created
        if temp_dir:
            shutil.rmtree(temp_dir)
        
    cleanup_after_processing()
    print("\nExtraction completed successfully.")
    end = time.time()  # Record the end time
    print(f"\nRuntime: {(end - start) / 60:.2f} minutes")  # Print the total runtime
    return None

# Main execution block
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Image Extraction of pdfs")
    parser.add_argument('--file', dest='file_name', required=False, help='The name of the PDF file to convert.')
    parser.add_argument('--bulk', action='store_true',  help='Enable bulk processing mode')
    parser.add_argument('--sample', action='store_true',  help='Enable sample papers only for processing')
    parser.add_argument('--input-dir', help='Directory containing PDF files')
    parser.add_argument('--output-dir', help='Directory for extracted results')
    args = parser.parse_args()


    pdf_files = pdf_files # commented out else in main for debuggin
    main(args)
    

