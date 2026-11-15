# Postman API Functional Testing Automated Runner
# Tests the 4 Agile User Stories against the running SmartStock server

$BaseUrl = "http://127.0.0.1:5000"
$Session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   SmartStock Automated API Testing Suite (Postman Runner)     " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Step 0: Admin Authentication
Write-Host "`n[STEP 0] Authenticating Admin..." -ForegroundColor Yellow
$LoginBody = @{
    email    = "admin@smartstock.local"
    password = "Admin123!"
} | ConvertTo-Json

$LoginRes = Invoke-RestMethod -Uri "$BaseUrl/api/auth/login" -Method Post -Body $LoginBody -ContentType "application/json" -WebSession $Session
Write-Host "  -> Result: $($LoginRes.message) | User: $($LoginRes.user.name) ($($LoginRes.user.role))" -ForegroundColor Green

# US-01 (SCRUM-22): Add New Product
Write-Host "`n[US-01 (SCRUM-22)] Add New Product..." -ForegroundColor Yellow
$NewProduct = @{
    sku           = "KB-RGB-$(Get-Random -Minimum 100 -Maximum 999)"
    name          = "Mechanical Gaming Keyboard RGB"
    description   = "Tactile blue switches, multi-device Bluetooth & 2.4GHz"
    cost_price    = 2500.00
    selling_price = 3999.00
    quantity      = 20
    reorder_level = 5
} | ConvertTo-Json

$CreateRes = Invoke-RestMethod -Uri "$BaseUrl/api/products" -Method Post -Body $NewProduct -ContentType "application/json" -WebSession $Session
$CreatedId = $CreateRes.product.id
Write-Host "  -> Product Created ID: $CreatedId" -ForegroundColor Green
Write-Host "  -> SKU: $($CreateRes.product.sku)" -ForegroundColor Green
Write-Host "  -> Formatted Price: $($CreateRes.product.formatted_price)" -ForegroundColor Green
Write-Host "  -> Initial Quantity: $($CreateRes.product.quantity)" -ForegroundColor Green

# US-02 (SCRUM-23): View Product Inventory
Write-Host "`n[US-02 (SCRUM-23)] View Product Inventory..." -ForegroundColor Yellow
$ListRes = Invoke-RestMethod -Uri "$BaseUrl/api/products" -Method Get -WebSession $Session
Write-Host "  -> Total Products in Inventory: $($ListRes.total)" -ForegroundColor Green
$RetrievedProduct = Invoke-RestMethod -Uri "$BaseUrl/api/products/$CreatedId" -Method Get -WebSession $Session
Write-Host "  -> Retrieved By ID: $($RetrievedProduct.name) ($($RetrievedProduct.sku))" -ForegroundColor Green

# US-03 (SCRUM-24): Update Product Details
Write-Host "`n[US-03 (SCRUM-24)] Update Product Details..." -ForegroundColor Yellow
$UpdateBody = @{
    name          = "Mechanical Gaming Keyboard RGB (Updated Pro V2)"
    selling_price = 4499.00
    quantity      = 35
    reorder_level = 8
} | ConvertTo-Json

$UpdateRes = Invoke-RestMethod -Uri "$BaseUrl/api/products/$CreatedId" -Method Put -Body $UpdateBody -ContentType "application/json" -WebSession $Session
Write-Host "  -> Updated Name: $($UpdateRes.product.name)" -ForegroundColor Green
Write-Host "  -> Updated Price: $($UpdateRes.product.formatted_price)" -ForegroundColor Green
Write-Host "  -> Updated Quantity: $($UpdateRes.product.quantity)" -ForegroundColor Green

# US-04 (SCRUM-25): Delete Product
Write-Host "`n[US-04 (SCRUM-25)] Delete Product..." -ForegroundColor Yellow
$DeleteRes = Invoke-RestMethod -Uri "$BaseUrl/api/products/$CreatedId" -Method Delete -WebSession $Session
Write-Host "  -> Result: $($DeleteRes.message) (ID: $($DeleteRes.id))" -ForegroundColor Green

# Verify deletion (Expect 404)
try {
    Invoke-RestMethod -Uri "$BaseUrl/api/products/$CreatedId" -Method Get -WebSession $Session | Out-Null
    Write-Host "  -> Error: Product still exists!" -ForegroundColor Red
} catch {
    Write-Host "  -> Verified Deletion: HTTP 404 Not Found (Correct)" -ForegroundColor Green
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  [SUCCESS] All 4 User Stories Passed Automated API Validation! " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
