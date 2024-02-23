$cudaLibNvvpPath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\libnvvp"
$cudaBinPath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\bin"

$currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "Process")

if (-not $currentPath.Contains($cudaLibNvvpPath)) {
  $currentPath = $cudaLibNvvpPath + ";" + $currentPath
}

if (-not $currentPath.Contains($cudaBinPath)) {
  $currentPath = $cudaBinPath + ";" + $currentPath
}

[System.Environment]::SetEnvironmentVariable("PATH", $currentPath, "Process")


Write-Output "Added CUDA 12.1 for PyTorch."
