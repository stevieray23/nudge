# Zahnarzte Lead Enrichment - Phase 2 Scraper
# This script:
# 1. Visits each Gelbe Seiten URL to find the real clinic website
# 2. Visits each clinic website to find Impressum page
# 3. Extracts owner name + personal email from Impressum

$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Read batch file
$batchFile = "C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_3_websites.json"
$batch = Get-Content $batchFile -Raw | ConvertFrom-Json

$results = @()
$headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    "Accept-Language" = "de-DE,de;q=0.9"
    "Accept" = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

$processed = 0
$emailsFound = 0

foreach ($lead in $batch) {
    $processed++
    Write-Host "[$processed/$($batch.Count)] $($lead.clinic_name)..." -NoNewline
    
    $result = @{
        clinic_name = $lead.clinic_name
        address = $lead.address
        city = $lead.city
        website = $lead.website
        vorname = ""
        nachname = ""
        email = ""
        impressum_found = $false
        email_found = $false
        notes = ""
    }
    
    # Step 1: Find the real clinic website from Gelbe Seiten
    $clinicUrl = $null
    
    try {
        $gsResp = Invoke-WebRequest -Uri $lead.website -Headers $headers -TimeoutSec 15
        $gsHtml = $gsResp.Content
        
        # Look for website link in Gelbe Seiten page
        # Pattern: data-website or class containing "website" or "zur-website"
        if ($gsHtml -match 'data-website=[""]([^""]+)[""]') {
            $clinicUrl = $matches[1]
        }
        elseif ($gsHtml -match 'href=[""](https?://[^""]*(?:zahnarzt|zahnaerzte|praxis|dr\.)[^""]*)[""'][^>]*>(?:zur |Website|Webseite)') {
            $clinicUrl = $matches[1]
        }
        elseif ($gsHtml -match 'class=[""][^""]*website[^""]*[""][^>]*href=[""](https?://[^""]+)["""]') {
            $clinicUrl = $matches[1]
        }
        elseif ($gsHtml -match '"url"\s*:\s*"([^"]+)"' -and $matches[1] -notlike "*gelbeseiten*") {
            $clinicUrl = $matches[1]
        }
        
        # Also search JSON-LD for url field
        if (-not $clinicUrl) {
            $jsonLdMatch = [regex]::Match($gsHtml, '"url"\s*:\s*"([^"]+)"')
            if ($jsonLdMatch.Success -and $jsonLdMatch.Groups[1].Value -notlike "*gelbeseiten*") {
                $clinicUrl = $jsonLdMatch.Groups[1].Value
            }
        }
    }
    catch {
        $result.notes += "Error fetching Gelbe Seiten: $($_.Exception.Message); "
    }
    
    # Step 2: If we found a clinic URL, try to find Impressum
    if ($clinicUrl -and $clinicUrl -notlike "*gelbeseiten*") {
        Write-Host " [found: $clinicUrl]" -NoNewline
        
        $impressumUrl = $null
        $ownerName = $null
        $foundEmail = $null
        $impFound = $false
        
        # Try common Impressum paths
        $impressumPaths = @("/impressum", "/impressum/", "/impressum.html", "/legal", "/rechtliches", "/rechtliches/", "/anbieter", "/anbieterkennzeichnung")
        
        try {
            # First try root
            $clinicResp = Invoke-WebRequest -Uri $clinicUrl -Headers $headers -TimeoutSec 15
            $clinicHtml = $clinicResp.Content
            
            # Check if the root page itself has Impressum content
            if ($clinicHtml -match 'impressum|rechtliches|anbieterkennzeichnung' -and 
                $clinicHtml -match '(?:Inhaber|Geschäftsführer|Vetrieb|Zahnarzt|Dr\.)[^<]{5,100}') {
                $impFound = $true
                $clinicPageContent = $clinicHtml
            }
            
            # Try each impressum path
            foreach ($path in $impressumPaths) {
                $testUrl = $clinicUrl.TrimEnd('/') + $path
                try {
                    $impResp = Invoke-WebRequest -Uri $testUrl -Headers $headers -TimeoutSec 15
                    if ($impResp.StatusCode -eq 200) {
                        $impHtml = $impResp.Content
                        if ($impHtml -match 'impressum|rechtliches|anbieter|inhaber') {
                            $impressumUrl = $testUrl
                            $impFound = $true
                            $clinicPageContent = $impHtml
                            break
                        }
                    }
                }
                catch { }
            }
        }
        catch {
            $result.notes += "Error fetching clinic: $($_.Exception.Message); "
        }
        
        # Step 3: Extract owner name and email from impressum content
        if ($impFound -and $clinicPageContent) {
            # Extract email (prioritize non-generic emails)
            $emailPattern = '[\w\.\-]+@[\w\.\-]+\.[a-z]{2,}'
            $emails = [regex]::Matches($clinicPageContent, $emailPattern) | ForEach-Object { $_.Value } | Select-Object -Unique
            
            foreach ($e in $emails) {
                $lowered = $e.ToLower()
                if ($lowered -notmatch '^(info|kontakt|service|termin|booking|termine|rezeption|praxis|office|anmeldung|mail|post|hello|web|admin)@') {
                    $foundEmail = $e
                    break
                }
            }
            
            # Extract owner name
            # Look for Inhaber, Geschäftsführer, Zahnarzt patterns
            $namePatterns = @(
                '(?:Inhaber[in]*|Geschäftsführer[in]*|Vertreten durch|Betreiber)[:\s]+(?:Dr\.?\s*)?([A-ZÄÖÜ][a-zäöüß]+(?:\s+(?:von\s+)?[A-ZÄÖÜ][a-zäöüß]+){1,3})',
                '(?:Zahnarzt|Zahnärztin|Facharzt)[in]*\s*(?:Dr\.?\s*)?([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)',
                'Dr\.?\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
                '([A-ZÄÖÜ][a-zäöüß]{2,})\s+([A-ZÄÖÜ][a-zäöüß]{2,})\s*(?:\(|Dr\.|$|\s*Zahn)'
            )
            
            foreach ($pattern in $namePatterns) {
                $nameMatch = [regex]::Match($clinicPageContent, $pattern)
                if ($nameMatch.Success) {
                    $groups = $nameMatch.Groups
                    if ($groups.Count -ge 3) {
                        $ownerName = "$($groups[1].Value) $($groups[2].Value)"
                    }
                    break
                }
            }
            
            if ($foundEmail) {
                $result.email_found = $true
                $result.email = $foundEmail
                $emailsFound++
            }
            
            if ($ownerName) {
                $nameParts = $ownerName.Trim() -split '\s+'
                if ($nameParts.Count -ge 2) {
                    $result.vorname = $nameParts[0]
                    $result.nachname = $nameParts[-1]
                } else {
                    $result.nachname = $ownerName
                }
            }
        }
        
        $result.impressum_found = $impFound
        if ($impressumUrl) { $result.notes += "Impressum at: $impressumUrl; " }
    }
    else {
        $result.notes += "No clinic website found on Gelbe Seiten; "
        Write-Host " [no clinic website]" -NoNewline
    }
    
    $results += $result
    
    if ($result.email_found) {
        Write-Host " ✓ EMAIL: $($result.email)" -ForegroundColor Green
    } else {
        Write-Host " (no email)" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Summary ===" 
Write-Host "Processed: $processed"
Write-Host "Emails found: $emailsFound"

# Save results
$outputFile = "C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_3_enriched.json"
$results | ConvertTo-Json -Depth 10 | Set-Content -Path $outputFile -Encoding UTF8
Write-Host "Saved to: $outputFile"
