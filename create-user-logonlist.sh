InputDir=data
LDAPDir=$InputDir/LDAP/
LogonInputFile=$InputDir/logon.csv
OutputDir=parsed
OutputUsersDir=$OutputDir/users

UserId=$1

if [[ -n $UserId ]]; then
    echo $UserId
    OutputFile=$OutputUsersDir/$UserId.csv
    echo "date,pc,logon" > $OutputFile
    awk -F, '{
        if (NR != 1 && $3 ~ /'$UserId'$/) {
            sub(/[^0-9]+/, "", $4);
            print $2","$4","($5 ~ /Logon/);
        }
    }' $LogonInputFile >> $OutputFile
fi
    