import streamlit as st
import os
import time
from typing import Optional
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.logic import LogicManagementClient

# --- Azure Configuration ---
# Replace with your actual storage account URL and container name
# AZURE_STORAGE_ACCOUNT_URL = os.environ.get("AZURE_STORAGE_ACCOUNT_URL", "https://dsilassdatastorage.blob.core.windows.net")
AZURE_STORAGE_ACCOUNT_URL = "https://dsilassdatastorage.blob.core.windows.net"
CONTAINER_NAME = "dsilas-foundershub"

# Replace with your Azure subscription and resource group details
SUBSCRIPTION_ID = "c0346e61-0f1f-411a-8c22-32620deb01cf"
RESOURCE_GROUP_NAME = "dsileadallocationsystem"


# --- Azure Blob Storage Upload Function ---
def upload_to_azure_blob(file, filename: str) -> bool:
    """Uploads a file to Azure Blob Storage using DefaultAzureCredential."""
    if not AZURE_STORAGE_ACCOUNT_URL :
        st.error("Azure Storage Account URL is not configured.")
        return False
    try:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=AZURE_STORAGE_ACCOUNT_URL, credential=credential)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
        
        st.info(f"Uploading {filename} to Azure Blob Storage container: {CONTAINER_NAME}...")
        blob_client.upload_blob(file, overwrite=True)
        st.success(f"File '{filename}' uploaded successfully!")
        st.balloons()
        return True
    except Exception as e:
        st.error(f"Failed to upload file: {e}")
        return False

# --- Azure Logic App Status Check Function ---
def get_logic_app_status(workflow_name: str) -> Optional[dict]:
    """Gets the status of the last run for a given Logic App workflow name."""
    if not SUBSCRIPTION_ID or SUBSCRIPTION_ID == "<Your-Subscription-ID>":
        st.error("Azure Subscription ID is not configured.")
        return None
    try:
        credential = DefaultAzureCredential()
        logic_client = LogicManagementClient(credential, SUBSCRIPTION_ID)
        
        run_history = logic_client.workflow_runs.list(RESOURCE_GROUP_NAME, workflow_name)
        
        last_run = next(run_history, None)
        
        if last_run:
            error = last_run.error['message'] if last_run.error else None
            return {"status": last_run.status, "error": error, "name": last_run.name}
        else:
            return {"status": "No runs found", "error": None, "name": None}
            
    except Exception as e:
        st.error(f"Failed to get Logic App status: {e}")
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="Azure Data Loader", page_icon="📤", layout="centered")

st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #fff;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%);
        color: white;
        border-radius: 8px;
        font-size: 1.1em;
        padding: 0.5em 2em;
        border: none;
    }
    .stFileUploader>div>div {
        background: #fff3e0;
        border-radius: 8px;
        padding: 1em;
    }
    .stTextInput>div>div>input {
        background: #e3f2fd;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📤 Azure Data Loader")
tabs = st.tabs(["Upload File", "Check Logic App Status"])

# --- Tab 1: File Upload ---
with tabs[0]:
    st.header("Upload File to Azure Blob Storage")
    uploaded_file = st.file_uploader("Choose a file to upload", type=None)
    if uploaded_file is not None:
        filename = uploaded_file.name
        st.write(f"**Selected file:** {filename}")
        if st.button("Upload to Azure Blob Storage"):
            with st.spinner("Uploading file to Azure Blob Storage..."):
                success = upload_to_azure_blob(uploaded_file, filename)
            if success:
                st.success(f"File '{filename}' uploaded successfully!")
            else:
                st.error("Failed to upload file. Please try again.")

# --- Tab 2: Logic App Status ---
with tabs[1]:
    st.header("Check Azure Logic App Execution Status")
    workflow_name = st.text_input("Enter Logic App Workflow Name")
    if st.button("Check Status"):
        if workflow_name:
            with st.spinner(f"Checking status for '{workflow_name}'..."):
                status_info = get_logic_app_status(workflow_name)
            
            if status_info:
                st.write(f"**Status of last run (`{status_info['name']}`):** {status_info['status']}")
                if status_info["error"]:
                    st.error(f"Error: {status_info['error']}")
                elif status_info["status"] == "Succeeded":
                    st.success("Logic App run completed successfully!")
                elif status_info["status"] == "Running":
                    st.info("Logic App is still running. Please check again later.")
        else:
            st.warning("Please enter a Logic App Workflow Name.") 