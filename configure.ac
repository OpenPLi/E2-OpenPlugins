AC_INIT(plugins,0.0.1)
AM_INIT_AUTOMAKE(plugins,0.0.1)

TUXBOX_APPS_DIRECTORY

AM_PATH_PYTHON()
AC_PYTHON_DEVEL

AC_PROG_CXX

AC_ARG_WITH(boxtype,
	[  --with-boxtype=NAME box type [[none,dm7025,dm800...]]],
	[BOXTYPE="$withval"],[BOXTYPE="dm800"])

AC_SUBST(BOXTYPE)
AC_DEFINE_UNQUOTED(BOXTYPE,"$BOXTYPE",[box type])

AM_CONDITIONAL([DM8000], [test "$BOXTYPE" = "dm8000"])
AM_CONDITIONAL([DM7025], [test "$BOXTYPE" = "dm7025"])

AC_OUTPUT([
Makefile
PLi/Makefile
PLi/PPanel/Makefile
PLi/PPanel/data/Makefile
PLi/SoftcamSetup/Makefile
PLi/NFSServer/Makefile
PLi/Bitrate/Makefile
PLi/Bitrate/bitratetool/Makefile
PLi/NewsReader/Makefile
PLi/NewsReader/data/Makefile
PLi/RemoteControlChannel/Makefile
PLi/ScreenPosition/Makefile
PLi/StreamInterface/Makefile
PLi/SnmpAgent/Makefile
UPnP/Makefile
UPnP/UShare/Makefile
])
