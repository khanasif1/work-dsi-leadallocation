from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.logic import LogicManagementClient
import os

app = FastAPI()

# Azure configuration (replace with your values or use env vars)
AZURE_STORAGE_ACCOUNT_URL = os.environ.get("AZURE_STORAGE_ACCOUNT_URL", "https://dsilassdatastorage.blob.core.windows.net")
CONTAINER_MAP = {
    'founderhub': 'dsilas-foundershub',
    'crunchbase': 'dsilas-crunchbase',
    'others': 'dsilas-others',
}
SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", "c0346e61-0f1f-411a-8c22-32620deb01cf")
RESOURCE_GROUP_NAME = os.environ.get("AZURE_RESOURCE_GROUP_NAME", "dsileadallocationsystem")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), source: str = Form(...)):
    try:
        print("In upload_file")
        container = CONTAINER_MAP.get(source, 'dsilas-others')
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=AZURE_STORAGE_ACCOUNT_URL, credential=credential)
        blob_client = blob_service_client.get_blob_client(container=container, blob=file.filename)
        content = await file.read()
        blob_client.upload_blob(content, overwrite=True)
        return {"success": True, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logicapp-status/{workflow_name}")
async def logic_app_status(workflow_name: str):
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
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files from the React build
app.mount("/static", StaticFiles(directory="static"), name="static")
#******DeployTODO:Update before deployment to Azure*******
#app.mount("/static", StaticFiles(directory="static/static"), name="static")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse("static/index.html")

# CORS for local development (optional for deployed app)
# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 