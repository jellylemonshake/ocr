# Invoice Data Extractor with Llama 4

A powerful Streamlit application that extracts structured data from invoice images using Llama 4 Scout model via Groq API. The application processes invoice images through OCR and formats the extracted data into standardized SQL-ready tables.

![image](https://github.com/user-attachments/assets/01a6fc29-1871-4f77-8899-97e8b38bff98)
![image](https://github.com/user-attachments/assets/37332d7f-3fd7-4e63-9613-b8ed24d043aa)


## Features

* **Multi-image Processing**: Upload and process multiple invoice images simultaneously
* **Advanced OCR**: Uses Llama 4 Scout 17B model for accurate text extraction
* **Intelligent Image Processing**: Splits images into horizontal stripes with overlap for better OCR accuracy
* **Structured Output**: Generates two standardized tables:
  * **DETAILS TABLE**: Invoice header information (one row per invoice)
  * **ITEMS TABLE**: Line items with tax details (one row per item)
* **Real-time Processing**: Progress tracking with visual feedback
* **Session Management**: Caches processed results to avoid reprocessing
* **SQL-Ready Format**: Output formatted for direct database import

## Prerequisites

* **Python 3.7+** installed on your system
* **Internet connection** (mandatory for API calls)
* **Groq API subscription** for unlimited processing

## Installation

### 1. Clone or Download the Repository

Download the project files to your local machine.

### 2. Navigate to Project Directory

Open Windows PowerShell (or Terminal on Mac/Linux) and navigate to the project folder: cd "C:\Users\USER\Downloads\InvoiceOCR_llama4"
*Replace the path with your actual project directory*

### 3. Install Dependencies

Install the required Python packages: pip install -r requirements.txt


### 4. Set Up Environment Variables

Create a `.env` file in the project root directory and add your Groq API key:
GROQ_API_KEY=your_groq_api_key_here

**Note**: Get your API key from [Groq Console](https://console.groq.com/) and consider getting a subscription for unlimited processing.

## Usage

### 1. Start the Application

Run the Streamlit application: streamlit run app.py

### 2. Access the Web Interface

The application will automatically open in your default browser. If not, navigate to the URL displayed in the terminal (typically `http://localhost:8501`).

### 3. Upload Invoice Images

* Use the sidebar to upload invoice images (JPEG, PNG formats supported)
* Multiple files can be uploaded simultaneously
* Preview thumbnails will appear in the sidebar

### 4. Process and View Results

* The application automatically processes new uploads
* Progress is displayed with real-time status updates
* Results appear as structured tables below each processed image

## Output Format

The application generates two standardized tables:

### DETAILS TABLE
Contains invoice header information including:
* Invoice details (number, date, currency)
* Seller information (name, GSTIN, address, contact)
* Billing information (name, GSTIN, address, contact)
* Shipping information (name, GSTIN, address, contact)
* Financial totals (subtotal, tax, total)
* Payment terms and due date
* Transport details (mode, transporter, vehicle info)

### ITEMS TABLE
Contains line item details including:
* Item name and quantity
* Unit price and total with tax
* Tax information (name, rate, value)
* Associated invoice number

## Technical Details

### Dependencies

* **streamlit**: Web application framework
* **groq**: Groq API client
* **python-dotenv**: Environment variable management
* **langchain-groq**: LangChain integration for Groq
* **langchain_community**: Additional LangChain components
* **pillow**: Image processing library
* **numpy**: Numerical computing support

### Models Used

* **OCR Model**: `meta-llama/llama-4-scout-17b-16e-instruct`
* **Formatting Model**: `llama-3.3-70b-versatile`

### Image Processing

* Images are automatically resized (120% scaling)
* Split into 5 horizontal stripes with 10% overlap
* Each stripe is processed independently for better accuracy
* Results are combined and formatted into structured tables

## Project Structure
![image](https://github.com/user-attachments/assets/cefdfe01-aa1c-4a94-873b-756a4a011631)

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your Groq API key is correctly set in the `.env` file
2. **Installation Issues**: Make sure Python 3.7+ is installed and pip is up to date
3. **Processing Errors**: Check your internet connection and API quota
4. **Image Upload Issues**: Ensure images are in JPEG or PNG format

### Support

For issues or questions:
* Check that all dependencies are properly installed
* Verify your Groq API key is valid and has sufficient quota
* Ensure images are clear and readable for better OCR results

## License

This project is provided as-is for educational and commercial use.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.






