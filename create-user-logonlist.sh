InputDir=data
LDAPDir=$InputDir/LDAP/
LogonInputFile=$InputDir/logon.csv
OutputDir=parsed
OutputUsersDir=$OutputDir/users

UserId=$1

if [[ -n $UserId ]]; then
    echo $UserId
    OutputFile=$OutputUsersDir/$UserId.csv
    echo "day,mon,yr,hr,min,sec,pc,logon" > $OutputFile
    awk -F, '{
        if (NR != 1 && $3 ~ /'$UserId'$/) {
            split($2, a, " ")
            split(a[1], d, "/")
            split(a[2], t, ":")
            sub(/[^0-9]+/, "", $4);
            print d[1]","d[2]","d[3]","t[1]","t[2]","t[3]","$4","($5 ~ /Logon/);
        }
    }' $LogonInputFile >> $OutputFile
fi
    