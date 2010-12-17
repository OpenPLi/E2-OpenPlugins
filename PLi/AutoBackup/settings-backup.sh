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

echo "Backup to ${BACKUPDIR}"

mkdir -p ${BACKUPDIR}/backup/enigma2
cp -a /etc/enigma2/* ${BACKUPDIR}/backup/enigma2/

[ -d /home/root/.ssh ] && cp -rp /home/root/.ssh ${BACKUPDIR}/backup/
cp -p /etc/dropbear/dropbear_rsa_host_key ${BACKUPDIR}/backup/

if [ -f ${PLI_BACKUPFILE} ]
then
for file in $(cat ${PLI_BACKUPFILE})
do
        [ -f /etc/$file ] && cp -p /etc/$file ${BACKUPDIR}/backup/
done
fi

if [ -f ${USER_BACKUPFILE} ]
then
for file in $(cat ${USER_BACKUPFILE})
do
        [ -f $file ] && cp -p $file ${BACKUPDIR}/backup/
done
fi

cp /etc/samba/smb.conf ${BACKUPDIR}/backup/

if [ -d /etc/tuxbox/config ]
then
	mkdir -p ${BACKUPDIR}/backup/tuxbox
	cp -rp /etc/tuxbox/config ${BACKUPDIR}/backup/tuxbox/
fi

crontab -l > /tmp/crontab 2> /dev/null && cp -f /tmp/crontab ${BACKUPDIR}/backup/crontab
rm -f /tmp/crontab

# todo: other cams?
# todo: network?
# todo: default?

touch ${BACKUPDIR}/backup/.timestamp

true
