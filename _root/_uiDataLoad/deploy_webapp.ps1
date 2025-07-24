# PowerShell script to build and deploy the React frontend and FastAPI backend to Azure Web App

# --- Configuration ---
$resourceGroup = "dsileadallocationsystem"
$appName = "dsilead-admin-app" # Change to a unique name
$location = "australiaeast"
$pythonVersion = "3.11"
$appServicePlanName = "dsilead-admin-appplan"

# --- 1. Build React Frontend ---
# ***********Be out side _root folder
Write-Host "Building React frontend..." -ForegroundColor Cyan
Push-Location -Path "./_root/_uiDataLoad/frontend"
npm install
npm run build
Pop-Location
Write-Host "React build complete." -ForegroundColor Green

# --- 2. Stage files for deployment ---
Write-Host "Staging files for deployment..." -ForegroundColor Cyan
$stagingDir = "./deployment_package"
if (Test-Path $stagingDir) {
    Remove-Item -Recurse -Force $stagingDir
}
New-Item -ItemType Directory -Path $stagingDir

# Copy FastAPI backend
Copy-Item -Path "./_root/_uiDataLoad/fastapi_backend.py" -Destination "$stagingDir/main.py"
Copy-Item -Path "./_root/_uiDataLoad/requirements.txt" -Destination "$stagingDir/requirements.txt"

# Copy React build output to a 'static' folder
Copy-Item -Recurse -Path "./_root/_uiDataLoad/frontend/build" -Destination "$stagingDir/static"

Write-Host "Staging complete." -ForegroundColor Green

# --- 3. Create Azure Resources is not already exist ---
Write-Host "Creating Azure resources..." -ForegroundColor Cyan
# az group create --name $resourceGroup --location $location

#az appservice plan create --name $appServicePlanName --resource-group $resourceGroup --sku B1 --is-linux
#***This is working 
#az webapp create --resource-group $resourceGroup --plan $appServicePlanName --name $appName --runtime "PYTHON:$pythonVersion" --startup-file "uvicorn main:app --host 0.0.0.0 --port 8000"
# Add App setting
#SCM_DO_BUILD_DURING_DEPLOYMENT = true

#az webapp config set --resource-group $resourceGroup --name $appName --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker fastapi_backend:app"
#az webapp config set --resource-group dsileadallocationsystem --name $appName --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker fastapi_backend:app"

# --- 4. Deploy to Azure ---
Write-Host "Zipping and deploying application..." -ForegroundColor Cyan
$zipFile = "deployment.zip"
if (Test-Path $zipFile) {
    Remove-Item $zipFile
}
Push-Location -Path $stagingDir
Compress-Archive -Path ".\*" -DestinationPath "../$zipFile"
Pop-Location

az webapp deploy --resource-group $resourceGroup --name $appName --src-path $zipFile --type zip

# --- 5. Clean up ---
Write-Host "Cleaning up local staging files..." -ForegroundColor Cyan
cd <ur path>\work-dsi-leadallocation
Remove-Item -Recurse -Force $stagingDir
Remove-Item $zipFile

Write-Host "Deployment complete! Your app is available at: https://$appName.azurewebsites.net" -ForegroundColor Green 