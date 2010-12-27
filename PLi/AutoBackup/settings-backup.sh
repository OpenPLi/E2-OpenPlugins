#! /bin/sh
# Backup files to harddisk backup dir

if [ -z "$1" ]
then
	echo "No destination, aborting."
	exit 1
fi
BACKUPDIR="$1"
PLI_BACKUPFILE=/usr/lib/enigma2/python/Plugins/PLi/AutoBackup/backup.cfg
USER_BACKUPFILE=/etc/backup.cfg
USER_AUTOINSTALL=/etc/autoinstall
INSTALLED=/etc/installed
TEMP_INSTALLED=/tmp/installed
RESTORE_TEMP=/tmp/restore.cfg

if [ -x /usr/bin/opkg ]
then
	IPKG=/usr/bin/opkg
else
	IPKG=ipkg
fi

echo "Backup to ${BACKUPDIR}/backup/"

if [ -f ${PLI_BACKUPFILE} ] 
then
	for file in $(cat ${PLI_BACKUPFILE})
	do
		if [ -f $file ]
		then
			echo $file >> ${RESTORE_TEMP}
		else
			if [ -d $file ]
			then
			echo $file >> ${RESTORE_TEMP}
			fi
		fi
	done
fi

if [ -f ${USER_BACKUPFILE} ] 
then
	for file in $(cat ${USER_BACKUPFILE})
	do
		if [ -f $file ]
		then
			echo $file >> ${RESTORE_TEMP}
		else
			if [ -d $file ]
			then
			echo $file >> ${RESTORE_TEMP}
			fi
		fi
	done
fi

cp -f /etc/passwd /tmp && echo /tmp/passwd >> ${RESTORE_TEMP}

if [ -f /etc/fstab ]
then
  for fstype in cifs nfs swap
  do
    grep -q " ${fstype} " /etc/fstab || grep " ${fstype} " /etc/fstab >> /tmp/fstab
  done
echo /tmp/fstab >> ${RESTORE_TEMP} 
fi

crontab -l > /tmp/crontab 2> /dev/null && echo /tmp/crontab >> ${RESTORE_TEMP}

tar -czf ${BACKUPDIR}/backup/PLi-AutoBackup.tar.gz --files-from=/tmp/restore.cfg 2> /dev/null

if [ -f ${INSTALLED} ]
then
	echo "Generating ${BACKUPDIR}/backup/autoinstall"
	${IPKG} list_installed | cut -d ' ' -f 1 > ${TEMP_INSTALLED}
	diff ${INSTALLED} ${TEMP_INSTALLED} | grep '+' | grep -v '@' | grep -v '+++' | sed 's/^+//' > ${BACKUPDIR}/backup/autoinstall
	
	if [ -f ${USER_AUTOINSTALL} ] 
	then
		cat ${USER_AUTOINSTALL} >> ${BACKUPDIR}/backup/autoinstall
	fi
fi

# todo: other cams?
# todo: network?
# todo: default?

touch ${BACKUPDIR}/backup/.timestamp
rm -f /tmp/restore.cfg
rm -f /tmp/crontab
rm -f /tmp/fstab
rm -f /tmp/passwd
rm -f ${TEMP_INSTALLED}
true
