# Picaxe-OCR

## Overview

This software tool is designed to programmatically process, analyze and extract images from PDF files(including scanned pdfs) using PaddleOCR, LayoutParser, and other image processing libraries. It includes a pipeline of scripts to remove tables, extract text, and clean up images.

There are 2 Options: 
1. With the program cloned from this repo
2. With a Docker image


## OPTION 1: Running the software

### Setup Instructions

#### 1. Clone the Repository

```bash
git clone -b picAxe_paddleocr https://github.com/acguerr1/imageextraction.git <local-destination-name>
cd <local-destination-name>
```

#### 2. Set Up the Virtual Environment

Create and activate a virtual environment:

```bash
python -m venv <venv-name>
source <venv-name>/bin/activate  # On macOS/Linux
.\<venv-name>\Scripts\activate  # On Windows
```

#### 3. Install Dependencies
Run this to install python dependencies and models needed

```bash
python ./src/install_pkgs.py
```

#### 4. Install Poppler (required for pdf2image):

**For macOS/Linux with Homebrew:**
1. Install Homebrew if you don't have it: 
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
2. Install poppler
    ```bash
    brew install poppler
    ```
**For Windows:**

1. Install Chocolatey from this website:  
    [https://chocolatey.org/](https://chocolatey.org/)
2. Run:
    ```bash
    choco install poppler
    ```
3. Add the bin/ folder to your system's PATH.



### Running the Pipeline
With specified input and output dirs:

```
python main.py --input-dir ./<YOUR_INPUT_DIR_NAME> --output-dir ./<YOUR_OUTPUT_DIR_NAME>
```
    
To run the entire processing pipeline with sample files, use the following command:

```bash
python main.py --bulk
python main.py --sample
python main.py --file filename
```

Outputs will be in these directories:

```
data/images/extracted_images
data/images/tables
```


This will execute the scripts in the following order:

1. **convert_pdfs_to_images.py** - Converts PDF file pages to PNG images.
2. **crop_borders.py** - Crops the borders of the pages if they have scan borders.
3. **remove_tables.py** - Removes tables from the images.
4. **remove_text.py** - Removes text from the images.
5. **select_target_images.py** - Selects target images for further processing.
6. **extract_and_save_images.py** - Extracts and saves images based on the processed results.

### Notes

- Ensure that the virtual environment is activated before running any scripts.
- Modify paths and configurations as needed in the `config.py` file located in the `src/` directory.



## OPTION 2: Pull and Run Docker Image

1. Run this to pull image: 
    ```bash
    docker pull brunofelalaga/picaxe-paddleocr:v1
    ```

2. Go to  Project Folder. 
    ```bash
    cd /path/to/your/project_folder
    ```

3. Run the Docker Container for any input location or either of the 3 modes [sample/bulk/file]:

    With specified input/output dirs outside sample and bulk folders:

    ```bash
    docker run --rm \
                -v $(pwd)/INPUT_DIR:/app/INPUT_DIR \
                -v $(pwd)/OUTPUT_DIR:/app/OUTPUT_DIR \
                brunofelalaga/picaxe-paddleocr:v1 \
                --input-dir ./INPPUT_DIR --output-dir ./OUTPUT_DIR
    ```

    
    For --sample mode:

    ```bash
    docker run -it --rm \
                    -v $(pwd)/data/pdf_files/sample_papers:/app/data/pdf_files/sample_papers \
                    -v $(pwd)/data/images:/app/data/images \
                    brunofelalaga/picaxe-paddleocr:v1 --sample
    ```

    For --bulk mode:

    ```bash
    docker run -it --rm \
                    -v $(pwd)/data/pdf_files/bulk_papers:/app/data/pdf_files/bulk_papers \
                    -v $(pwd)/data/images:/app/data/images \
                    brunofelalaga/picaxe-paddleocr:v1 --bulk
    ```

    For --file :

    ```bash
    docker run -it --rm \
                    -v $(pwd)/data/pdf_files/sample_papers:/app/data/pdf_files/sample_papers \
                    -v $(pwd)/data/images:/app/data/images \
                    brunofelalaga/picaxe-paddleocr:v1 --file Ketchem.pdf
    ```
    
    Outputs will be in these directories:

    ```
    data/images/extracted_images
    data/images/tables
    ```
    

   


#### Data Folder Structure
```
data/
├── pdf_files/
│   ├── sample_papers/     # PDFs for --sample and --file modes
│   └── bulk_papers/       # PDFs for --bulk mode
├── images/                # Output images (auto-created)
└── logs/                  # Log files (auto-created)
```
