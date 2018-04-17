InputDir=data
LDAPDir=$InputDir/LDAP/
LogonInputFile=$InputDir/logon.csv
OutputDir=parsed
UserListFile=$OutputDir/users.txt
TempFile=$OutputDir/temp.txt

mkdir $OutputDir

# Reading User List
> $UserListFile
for LDAPFile in $(ls $LDAPDir); do
    awk -F, '{
        if (NR != 1) print $2
    }' $LDAPDir$LDAPFile >> $UserListFile
done
sort $UserListFile | uniq > $TempFile
mv $TempFile $UserListFile
echo "User list created"