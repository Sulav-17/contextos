param(
    [Parameter(Mandatory = $true)]
    [string] $SiteUrl,

    [Parameter(Mandatory = $true)]
    [string] $ApiUrl
)

$ErrorActionPreference = "Stop"

function Test-Endpoint {
    param(
        [string] $Name,
        [string] $Url,
        [int[]] $AllowedStatusCodes = @(200)
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -MaximumRedirection 0 -UseBasicParsing
        $statusCode = [int] $response.StatusCode
    } catch {
        if ($_.Exception.Response -eq $null) {
            throw
        }
        $statusCode = [int] $_.Exception.Response.StatusCode
    }
    if ($AllowedStatusCodes -notcontains $statusCode) {
        throw "$Name returned $statusCode for $Url"
    }
    Write-Host "$Name ok ($statusCode)"
}

$site = $SiteUrl.TrimEnd("/")
$api = $ApiUrl.TrimEnd("/")

Test-Endpoint -Name "public site" -Url $site
Test-Endpoint -Name "login route" -Url "$site/login"
Test-Endpoint -Name "api health" -Url "$api/health"
Test-Endpoint -Name "api readiness" -Url "$api/ready"

Write-Host "Smoke checks passed."
