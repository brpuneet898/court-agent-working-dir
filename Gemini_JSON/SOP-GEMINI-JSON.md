**Document Title:** Standard Operating Procedure (SOP) for Generating JSON from PDFs using Gemini API Calls

**Document Number:** SOP-GEMINI-001  
**Version:** 1.0  
**Effective Date:** July 8, 2025  
**Prepared by:** [Your Team Name]  
**Approved by:** [Approver Name]

---

## 1. Purpose
This SOP describes the standardized process for using the `Gemini_JSON.ipynb` Jupyter Notebook to convert a collection of PDF documents (provided as a ZIP file) into structured JSON outputs by leveraging the Gemini API. The procedure ensures consistent, reliable, and reproducible results for all users.

## 2. Scope
This document applies to all team members and external collaborators who need to process PDF files into JSON format using the Gemini API. It covers environment setup, input preparation, execution of the notebook, validation of outputs, and troubleshooting.

## 3. Definitions
- **Gemini API:** A hypothetical API service used to extract and structure data from PDF documents into JSON format.
- **Notebook:** The Jupyter Notebook file `Gemini_JSON.ipynb` containing code and instructions.
- **ZIP Archive:** A compressed file containing one or more PDF documents.

## 4. Roles and Responsibilities
- **Operator:** Responsible for executing the notebook, monitoring progress, and validating outputs.
- **Maintainer:** Responsible for updating the notebook, dependencies, and this SOP as needed.
- **Approver:** Reviews and approves revisions to this document.

## 5. Prerequisites
1. **System Requirements:**
   - Operating System: Windows, macOS, or Linux  
   - Python 3.8 or higher  
   - At least 4 GB RAM  
2. **Software and Libraries:**
   - Jupyter Notebook or Jupyter Lab  
   - Dependencies listed in `requirements.txt` (e.g., `requests`, `zipfile`, `pypdf2`, `dotenv`)  
   - Gemini API credentials (API key and endpoint URL)  
3. **Access:**
   - Access to the ZIP file containing PDFs  
   - Internet connection to reach the Gemini API service  
4. **Configuration:**
   - A `.env` file in the working directory with the following variables:
     ```dotenv
     GEMINI_API_KEY=your_api_key_here
     ```

## 6. Procedure

### 6.1. Environment Setup
1. **Clone Repository or Obtain Files:**
   - Download or clone the project directory containing `Gemini_JSON.ipynb` and `requirements.txt`.  
2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure API Credentials:**
   - Ensure the `.env` file is present and correctly populated (see Section 5.4).

### 6.2. Preparing Input Files
1. **Locate ZIP Archive:**
   - Place the ZIP file (e.g., `pdf_documents.zip`) in the working directory.  
2. **Unzip the Archive:**
   - The notebook will handle unzipping automatically, but verify that PDFs are extracted into a folder named `pdfs/`.

### 6.3. Executing the Notebook
1. **Launch Jupyter Notebook:**
   ```bash
   jupyter notebook Gemini_JSON.ipynb
   ```
2. **Review and Run Cells Sequentially:**
   - **Cell 1:** Load environment variables and dependencies.  
   - **Cell 2:** Unzip PDF archive and list file paths.  
   - **Cell 3:** Initialize Gemini API client using the API key and endpoint.  
   - **Cell 4:** Loop through each PDF file, send API requests, and collect JSON responses.  
   - **Cell 5:** Save individual JSON outputs to an `output/` directory, preserving original PDF filenames.  
   - **Cell 6:** (Optional) Aggregate all JSON responses into a single master JSON file.  
3. **Monitor for Errors:**
   - Check console output for any failed API calls or file I/O errors.

### 6.4. Validating Outputs
1. **Output Directory:**
   - Confirm that an `output/` folder exists and contains one `.json` file per PDF.  
2. **Schema Compliance:**
   - Optionally, validate each JSON against a predefined JSON Schema (if available).  
3. **Spot-Check Samples:**
   - Open a few JSON files to verify correct extraction of key fields.

### 6.5. Troubleshooting
- **Failed API Request:**
  - Check network connectivity and verify API endpoint URL.  
  - Confirm that the API key in `.env` is valid and not expired.  
- **Missing PDFs after Unzip:**
  - Ensure the ZIP file is not corrupted and contains PDFs at the root level.  
- **Permission Errors:**
  - Verify read/write permissions on the working directory and subfolders.