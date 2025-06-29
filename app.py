import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from langchain_groq import ChatGroq
import base64
import io
from time import sleep
import re

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DETAILS_FIELDS = [
    "InvoiceNumber", "InvoiceDate", "SellerName", "SellerGSTIN", "SellerUIN",
    "SellerAddress", "SellerContact", "BilledToName", "BilledToGSTIN", "BilledToUIN",
    "BilledToAddress", "BilledToContact", "ShippedToName", "ShippedToGSTIN", "ShippedToUIN",
    "ShippedToAddress", "ShippedToContact", "Subtotal", "TotalTax", "TotalWithTax",
    "Currency", "PaymentTerms", "DueDate",
    "TransportMode", "TransporterName", "TransporterID", "VehicleType", "VehicleNumber"
]
ITEM_FIELDS = [
    "InvoiceNumber", "ItemName", "Quantity", "UnitPrice", "TaxName", "TaxRate", "TaxValue", "TotalWithTax"
]
ADDRESS_FIELDS = {
    "SellerAddress", "SellerContact", "BilledToAddress", "BilledToContact",
    "ShippedToAddress", "ShippedToContact", "TransporterName", "VehicleType"
}

def encode_image_pil(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image = image.convert("RGB")
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def split_image_into_horizontal_stripes(image: Image.Image, stripe_count: int = 5, overlap: float = 0.1):
    width, height = image.size
    stripe_height = height // stripe_count
    overlap_height = int(stripe_height * overlap)
    stripes = []
    for i in range(stripe_count):
        upper = max(i * stripe_height - overlap_height, 0)
        lower = min((i + 1) * stripe_height + overlap_height, height)
        stripe = image.crop((0, upper, width, lower))
        stripes.append(stripe)
    return stripes

def ocr(image: Image.Image, model: str = "meta-llama/llama-4-scout-17b-16e-instruct") -> str:
    groq_llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=model,
        temperature=0
    )
    image_data_url = f"data:image/jpeg;base64,{encode_image_pil(image)}"
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": (
                    "Extract all printed and handwritten text from this invoice image. "
                    "Be precise and do not miss any details."
                )},
                {"type": "image_url", "image_url": {"url": image_data_url}}
            ]
        }
    ]
    response = groq_llm.invoke(messages)
    return response.content.strip()

def format_to_table(markdown_runs: list, model: str = "llama-3.3-70b-versatile") -> str:
    groq_llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=model,
        temperature=0
    )
    combined_markdown = "\n\n".join(markdown_runs)
    prompt = (
        "You are provided with OCR outputs from invoice images. "
        "Extract and organize the data into two standardized tables for SQL import. "
        "If a value is missing, use NULL. For addresses or contact fields, replace any commas with spaces. "
        "Tables:\n\n"
        "1. DETAILS TABLE (one row per invoice):\n"
        "| Field | Value |\n"
        "|--------------------------|-------|\n"
        "| InvoiceNumber            |       |\n"
        "| InvoiceDate              |       |\n"
        "| SellerName               |       |\n"
        "| SellerGSTIN              |       |\n"
        "| SellerUIN                |       |\n"
        "| SellerAddress            |       |\n"
        "| SellerContact            |       |\n"
        "| BilledToName             |       |\n"
        "| BilledToGSTIN            |       |\n"
        "| BilledToUIN              |       |\n"
        "| BilledToAddress          |       |\n"
        "| BilledToContact          |       |\n"
        "| ShippedToName            |       |\n"
        "| ShippedToGSTIN           |       |\n"
        "| ShippedToUIN             |       |\n"
        "| ShippedToAddress         |       |\n"
        "| ShippedToContact         |       |\n"
        "| Subtotal                 |       |\n"
        "| TotalTax                 |       |\n"
        "| TotalWithTax             |       |\n"
        "| Currency                 |       |\n"
        "| PaymentTerms             |       |\n"
        "| DueDate                  |       |\n"
        "| TransportMode            |       |\n"
        "| TransporterName          |       |\n"
        "| TransporterID            |       |\n"
        "| VehicleType              |       |\n"
        "| VehicleNumber            |       |\n"
        "\n"
        "2. ITEMS TABLE (one row per item):\n"
        "| InvoiceNumber | ItemName | Quantity | UnitPrice | TaxName | TaxRate | TaxValue | TotalWithTax |\n"
        "\n"
        "Instructions:\n"
        "- Output ONLY the two tables in markdown format (no explanations).\n"
        "- Use 'NULL' for missing values.\n"
        "- For address/contact fields, replace commas with spaces.\n"
        "- InvoiceNumber must be present in both tables.\n"
        "- For each item, if there are multiple taxes, list all TaxName, TaxRate, TaxValue in the respective cell, separated by '; '. Do NOT split into multiple rows for the same item.\n"
        "- All amounts should be numbers (no currency symbols).\n"
        "\n"
        "Here is the OCR data:\n\n"
        + combined_markdown
    )
    messages = [{"role": "user", "content": prompt}]
    response = groq_llm.invoke(messages)
    return response.content.strip()

# Session state for caching
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = {}
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

st.title("Invoice Data Extractor with Llama 4 – Tabular Output")
st.markdown("Upload invoice images. Extracted data is shown in standardized tables below each result.")

with st.sidebar:
    st.markdown("#### Upload Invoice Images")
    uploaded_files = st.file_uploader(
        "Upload multiple images (JPEG, PNG)", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) uploaded:**")
        for uploaded_file in uploaded_files:
            st.markdown(f"• {uploaded_file.name}")
        st.markdown("#### Image Previews")
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            image.thumbnail((200, 200))
            st.image(image, caption=uploaded_file.name, use_container_width=True)

current_file_names = [f.name for f in uploaded_files] if uploaded_files else []
new_files = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.processed_files:
            new_files.append(uploaded_file)

# Remove results for files that are no longer present
if uploaded_files:
    current_results = {}
    for file_name in current_file_names:
        if file_name in st.session_state.processed_results:
            current_results[file_name] = st.session_state.processed_results[file_name]
    st.session_state.processed_results = current_results
    st.session_state.processed_files = [f for f in st.session_state.processed_files if f in current_file_names]
else:
    st.session_state.processed_results = {}
    st.session_state.processed_files = []

if uploaded_files:
    if new_files:
        st.markdown(f"#### 🔄 Processing {len(new_files)} New Image(s)...")
        total_steps = sum([5 for _ in new_files]) + len(new_files)
        progress_bar = st.progress(0)
        status_container = st.empty()
        current_step = 0
        try:
            for file_idx, uploaded_file in enumerate(new_files):
                image = Image.open(uploaded_file)
                width, height = image.size
                image = image.resize((int(width * 1.2), int(height * 1.2)))
                stripes = split_image_into_horizontal_stripes(image)
                markdown_runs = []
                for i, stripe in enumerate(stripes, start=1):
                    current_step += 1
                    progress = min(current_step / total_steps, 1.0)
                    progress_bar.progress(
                        progress, 
                        text=f"Processing {uploaded_file.name} - Stripe {i}/{len(stripes)}"
                    )
                    status_container.markdown(
                        f"**File:** `{uploaded_file.name}` | Stripe: {i}/{len(stripes)}"
                    )
                    sleep(0.1)
                    try:
                        stripe_markdown = ocr(stripe)
                        markdown_runs.append(stripe_markdown)
                    except Exception as e:
                        st.error(f"OCR error: {e}")
                        raise
                current_step += 1
                progress = min(current_step / total_steps, 1.0)
                progress_bar.progress(
                    progress,
                    text=f"Formatting table for {uploaded_file.name}..."
                )
                status_container.markdown(f"**Formatting standardized tables for:** `{uploaded_file.name}`")
                try:
                    table_output = format_to_table(markdown_runs)
                    st.session_state.processed_results[uploaded_file.name] = table_output
                    st.session_state.processed_files.append(uploaded_file.name)
                except Exception as e:
                    st.error(f"Table formatting error: {e}")
                    raise
            progress_bar.progress(1.0, text="🎉 All images processed!")
            status_container.markdown("**✅ Processing complete!**")
            sleep(2)
            progress_bar.empty()
            status_container.empty()
        except Exception as e:
            st.error(f"Processing stopped: {e}")
            st.stop()

    st.markdown("#### 📋 Extracted Invoice Data")
    for uploaded_file in uploaded_files:
        if uploaded_file.name in st.session_state.processed_results:
            st.markdown(f"### 📄 Results for: `{uploaded_file.name}`")
            col1, col2 = st.columns([1, 2])
            with col1:
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, use_container_width=True)
            with col2:
                st.markdown("**Status:** ✅ Processed")
            table_output = st.session_state.processed_results[uploaded_file.name]
            st.markdown(table_output, unsafe_allow_html=True)
            st.markdown("---")
        else:
            st.markdown(f"### ⏳ Pending: `{uploaded_file.name}`")
            col1, col2 = st.columns([1, 2])
            with col1:
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, use_container_width=True)
            with col2:
                st.markdown("**Status:** 🔄 Pending...")
            st.markdown("---")
else:
    st.markdown("Upload images to start processing. Results will appear here as standardized tables below each result.")
