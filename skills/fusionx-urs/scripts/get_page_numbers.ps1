# Computes real per-bookmark ToC/LoF/LoT page numbers via a READ-ONLY Word-COM pass — never calls
# .Save() on the docx (a full open+Fields.Update()+Save() round-trip has been confirmed to strip
# explicit font overrides and table styles on re-normalization; this script only reads field
# results and closes without saving, which does not have that problem).
#
# Usage: powershell -File get_page_numbers.ps1 <path-to-docx> <output-mapping-file>
# Then:  python patch_page_numbers.py <path-to-docx> <output-mapping-file>
#
# Prerequisite: no other process has the file open (Word COM will fail to open a locked file).
# Check first: Get-Process WINWORD -ErrorAction SilentlyContinue

param(
    [Parameter(Mandatory=$true)][string]$DocPath,
    [Parameter(Mandatory=$true)][string]$OutPath
)

$DocPath = (Resolve-Path $DocPath).Path
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open($DocPath, [ref]$false, [ref]$true)
$doc.Repaginate()
$doc.Fields.Update()

$results = @()
foreach ($f in $doc.Fields) {
    if ($f.Type -eq 37) {  # wdFieldPageRef
        $code = $f.Code.Text
        if ($code -match '_Toc\d+') {
            $anchor = $Matches[0]
            $val = $f.Result.Text.Trim()
            $results += "$anchor=$val"
        }
    }
}
$doc.Close([ref]$false)
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null

# -Encoding utf8 in Windows PowerShell 5.1 writes a BOM, which corrupts the first key when Python
# reads it back — patch_page_numbers.py opens with encoding="utf-8-sig" specifically to tolerate
# this, so this is safe either way, but noting it here since it cost a debugging round once.
$results | Out-File -Encoding utf8 $OutPath
Write-Output "$($results.Count) page number(s) written to $OutPath"
