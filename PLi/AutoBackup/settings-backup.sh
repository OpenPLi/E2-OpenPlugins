#! /bin/sh
# Backup files to harddisk backup dir

if [ -z "$1" ]
then
	echo "No destination, aborting."
	exit 1
fi
BACKUPDIR="$1"

mkdir -p ${BACKUPDIR}/backup/enigma2
cp -a /etc/enigma2/* ${BACKUPDIR}/backup/enigma2/

[ -f /home/root/.ssh ] && cp -rp /home/root/.ssh ${BACKUPDIR}/backup/
cp /etc/dropbear/dropbear_rsa_host_key ${BACKUPDIR}/backup/ 

for file in CCcam.cfg CCcam.prio CCcam.channelinfo CCcam.providers radegast.cfg newsreader.conf NETcaster.conf resolv.conf fstab passwd
do
	[ -f /etc/$file ] && cp  /etc/$file ${BACKUPDIR}/backup/
done

cp /etc/samba/smb.conf ${BACKUPDIR}/backup/

[ -f /etc/tuxbox/config/newcamd.conf ] && cp /etc/tuxbox/config/newcamd.conf ${BACKUPDIR}/backup/

# todo: other cams?
# todo: crontab?
# todo: network?
# todo: default?
