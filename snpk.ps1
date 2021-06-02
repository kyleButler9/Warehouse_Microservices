#Access product key from serial number in the serialNumProductKeyTable.csv file
#1/12/2021 Kyle Butler

#directions: 
#to run script from a networked computer (tech station) here is an example command prompt line:
#	Powershell.exe -ExecutionPolicy Bypass -File //server/Programs/snpk/snpk.ps1 "03307512924311"

#you can copy paste the above, replacing the serial number with your own. The output wil be as follows:
#	for input Serial Num: 03307512924311   ProductKey is: Q6RMF8WNQ3JW62P6HM4DFM49E
#if the serial number is contained in the serialNumProductKeyTable.csv file and has an associated entry in the product key column.


#end snpk, begin datetime sync and time zone change...
#sync first then set time zone
net start w32time
$out = w32tm /resync
While ( $out[1].length -gt 40) 
{
	$out = w32tm /resync
	Write-Host("syncing time...")
}

#reset install folder
rm -r -fo C:\install
xcopy \\server\Programs\ks\install C:\install /i


#load the file of serial number product key pairings into a hash table
$serialNumToProductKeyTable = Import-Csv -Path $PSScriptRoot\serialNumProductKeyTable.csv
$hashTable = @{}
foreach ($row in $serialNumToProductKeyTable) {$hashTable[$row.serialNumber] =$row.productKey}

#pull the user input serial number into a variable for later use
[string]$serialNum = $args[0]

#check if the serial number the user input is in the table and print the appropriate output.
if ( -not $hashTable.containsKey("$serialNum") ) 
{
	Write-Host ("Serial Number " + $serialNum + " not in snpk/serialNumProductKeyTable.csv")
}
else
{
	Write-Host ("for input Serial Num: " + $serialNum + "   ProductKey is: " + $hashTable."$serialNum")
}

start C:\install\helper.exe
$time_to_sleep = 2
Write-Host("waiting " + $time_to_sleep + " seconds then resetting TimeZone")
Sleep($time_to_sleep)
#changes timezone to EST after helper changes it to central
$TZ = tzutil /g
While ($TZ -ne "Eastern Standard Time")
{
    tzutil /s "Eastern Standard Time"
    Write-Host("setting time zone...")
    $TZ = tzutil /g
}
Sleep($time_to_sleep)
#changes timezone to EST after helper changes it to central
$TZ = tzutil /g
While (1 -ne 2)
{$TZ = tzutil /g
While ($TZ -ne "Eastern Standard Time")
{
    tzutil /s "Eastern Standard Time"
    Write-Host("setting time zone...")
    $TZ = tzutil /g
}}