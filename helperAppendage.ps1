Add-OdbcDsn -Name "DEMO" -DriverName "PostgreSQL Unicode(x64)" -SetPropertyValue @("Server=IP","Database=DB","Port=PORT","Username=USER","Password=PASS") -DsnType "User"

$conn = New-Object -comobject ADODB.Connection
$conn.Open("DEMO")

#query computer serialnumber and then get id associated with this sn from the beta.computers table.
$dInfo = @{}
$info=$null
$info = wmic bios get serialNumber
$dInfo.add("bios_serialNumber",$info[2])
$snQuery = "SELECT pc_id
            FROM beta.computers)
            WHERE sn = "
$snQuery = $snQuery + "TRIM(LOWER('" + $dInfo["bios_serialNumber"]+"'));"
Write-Host $snQuery
$recordset=$conn.Execute($snQuery)
IF ($recordset.Fields[0].value -eq $null) {
    $outMsg = "Computer SN is not in DB"
    Write-Host $outMsg
    pause
    }
while ($recordset.EOF -ne $True)
{
    $dbInfo = @{}
    foreach ($field in $recordset.Fields)
    {
        $dbInfo.add($field.name,$field.value)
    }
   ''  # this line adds a line between records
$recordset.MoveNext()
}


$info = $null
$info = wmic diskdrive get serialNumber
$dInfo.add("diskdrive_serialNumber",$info[2])

$snQuery = "SELECT hd.sanitized,hd.hd_id 
            FROM beta.donatedgoods
            INNER JOIN beta.harddrives hd USING (hd_id)
            WHERE hd.hdsn = "

$snQuery = $snQuery + "TRIM(LOWER('" + $dInfo["diskdrive_serialNumber"]+"'));"

Write-Host $snQuery
$recordset=$conn.Execute($snQuery)


IF ($recordset.Fields[0].value -eq $null) {
    $outMsg = "HD is not in DB"
    Write-Host $outMsg
    pause
    }

while ($recordset.EOF -ne $True)
{
    $dbInfo = @{}
    foreach ($field in $recordset.Fields)
    {
        $dbInfo.add($field.name,$field.value)
    }
   ''  # this line adds a line between records
$recordset.MoveNext()
}
IF ($dbInfo["sanitized"] -eq 1) {
    Write-Host "HD is sanitized"
    $info = wmic diskdrive get model
    $dInfo.add("diskdrive_model",$info[2])
    $info = wmic diskdrive get size
    $dInfo.add("diskdrive_size",$info[2])
    $info = wmic bios get serialNumber
    $dInfo.add("bios_serialNumber",$info[2])
    $info = wmic bios get manufacturer
    $dInfo.add("bios_manufacturer",$info[2])
    $info = wmic cpu get name
    $dInfo.add("cpu_name",$info[2])

    $updateHDInfo = "UPDATE beta.harddrives " + `
                       "SET model = TRIM('" + $dInfo["diskdrive_model"].ToString() `
                    + "'), size = TRIM('" + $dInfo["diskdrive_size"].ToString() `
                    + "') WHERE hd_id =  " + $dbInfo["hd_id"].ToString() + ";"
    Write-Host $updateHDInfo
    $dummy =$conn.Execute($updateHDInfo)
    $updateDeviceInfo = "UPDATE beta.computers " + `
                        "SET cpu_name = TRIM('" + $dInfo["cpu_name"] + "') " + `
                        "WHERE sn = TRIM(" + $dInfo["bios_serialNumber"] + ") RETURNING device_id;"
    Write-Host $updateDeviceInfo
    $dummy = $conn.Execute($updateDeviceInfo)
    $markFinished = "INSERT INTO beta.refurbisheddevices(pc_id,hd_id) VALUES(" + 

}
ELSE {
    "HD is NOT logged as sanitized!!" 
    pause
    }


$conn.Close();
