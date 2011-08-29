#! /bin/sh
# Backup files to harddisk backup dir

AUTOINSTALL="no"

if [ -z "$1" ]
then
	echo "usage: $0 [-a] /path/to/destination"
	exit 1
fi
if [ "$1" == "-a" ]
then
	AUTOINSTALL="yes"
	shift
fi
BACKUPDIR="$1"
if [ -z "${BACKUPDIR}" ]
then
	echo "No destination, aborted"
	exit 1
fi
PLI_BACKUPFILE=/usr/lib/enigma2/python/Plugins/PLi/AutoBackup/backup.cfg
USER_BACKUPFILE=/etc/backup.cfg
USER_AUTOINSTALL=/etc/autoinstall
INSTALLED=/etc/installed
TEMP_INSTALLED=/tmp/installed
RESTORE_TEMP=/tmp/restore.cfg
MACADDR=`cat /sys/class/net/eth0/address | cut -b 1,2,4,5,7,8,10,11,13,14,16,17`

if [ -x /usr/bin/opkg ]
then
	IPKG=/usr/bin/opkg
else
	IPKG=ipkg
fi

echo "Backup to ${BACKUPDIR}/backup/"
mkdir -p ${BACKUPDIR}/backup

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
  for fstype in ' cifs ' ' nfs ' ' swap ' '^UUID=' '^LABEL='
  do
    grep "${fstype}" /etc/fstab >> /tmp/fstab
  done
  [ -s /tmp/fstab ] && echo /tmp/fstab >> ${RESTORE_TEMP} 
fi

crontab -l > /tmp/crontab 2> /dev/null && echo /tmp/crontab >> ${RESTORE_TEMP}

tar -czf ${BACKUPDIR}/backup/PLi-AutoBackup${MACADDR}.tar.gz --files-from=/tmp/restore.cfg 2> /dev/null
if [ ! -z "${MACADDR}" ]
then
	ln -f -s PLi-AutoBackup${MACADDR}.tar.gz ${BACKUPDIR}/backup/PLi-AutoBackup.tar.gz || cp -p ${BACKUPDIR}/backup/PLi-AutoBackup${MACADDR}.tar.gz ${BACKUPDIR}/backup/PLi-AutoBackup.tar.gz  
fi

if [ "${AUTOINSTALL}" == "yes" -a -f ${INSTALLED} ]
then
	echo "Generating ${BACKUPDIR}/backup/autoinstall${MACADDR}"
	${IPKG} list_installed | cut -d ' ' -f 1 > ${TEMP_INSTALLED}
	diff ${INSTALLED} ${TEMP_INSTALLED} | grep '+' | grep -v '@' | grep -v '+++' | sed 's/^+//' > ${BACKUPDIR}/backup/autoinstall${MACADDR}
	if [ -f ${USER_AUTOINSTALL} ]
	then
		for plugin in `cat ${USER_AUTOINSTALL}`
		do
			cp -p ${BACKUPDIR}/backup/autoinstall /tmp/autoinstall
			pluginname=`echo ${plugin} | sed 's/_.*//' | sed -re 's/^.+\///'`
			cat /tmp/autoinstall | grep -v "$pluginname$" > ${BACKUPDIR}/backup/autoinstall${MACADDR}
		done
		cat ${USER_AUTOINSTALL} >> ${BACKUPDIR}/backup/autoinstall${MACADDR}
	fi
	if [ ! -z "${MACADDR}" ]
	then
		ln -f -s autoinstall${MACADDR} ${BACKUPDIR}/backup/autoinstall || cp -p ${BACKUPDIR}/backup/autoinstall${MACADDR} ${BACKUPDIR}/backup/autoinstall
	fi
fi

touch ${BACKUPDIR}/backup/.timestamp
rm -f /tmp/restore.cfg
rm -f /tmp/crontab
rm -f /tmp/fstab
rm -f /tmp/passwd
rm -f ${TEMP_INSTALLED}
true
