# Run with Windows PowerShell 5.1 and PowerShell 7. No Docker or network needed.
$ErrorActionPreference = 'Stop'
$DeployDir = Split-Path -Parent $PSScriptRoot
$ScriptPath = Join-Path $DeployDir 'build-and-export.ps1'
$ParseTokens = $null
$ParseErrors = $null
$Ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $ScriptPath, [ref]$ParseTokens, [ref]$ParseErrors
)
if ($ParseErrors.Count -gt 0) {
    $ParseErrors | ForEach-Object {
        Write-Host ('Line {0}: {1}' -f $_.Extent.StartLineNumber, $_.Message)
    }
    throw 'The build script must parse using the host PowerShell file encoding.'
}

# Assert that the file parser retains Chinese completion messages, not mojibake.
$CompletionWord = ([string][char]0x5B8C) + ([string][char]0x6210)
$CompletionMessages = $Ast.FindAll({
    param($Node)
    $Node -is [System.Management.Automation.Language.StringConstantExpressionAst] -and
        $Node.Value.Contains($CompletionWord)
}, $true)
if ($CompletionMessages.Count -eq 0) {
    throw 'The build script completion messages were decoded incorrectly.'
}
Write-Host ('PASS: script parses and preserves Chinese text on PowerShell {0}' -f $PSVersionTable.PSVersion)
