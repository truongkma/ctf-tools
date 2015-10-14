# Path to Watcom C
WATCOM=o:/watcom

CC = wcc386 /ohx 
MAKE = make

default:
	@echo Usage: $(MAKE) -f makefile.wat target
	@echo where target is one of: os2 dpmi win32

#for OS/2 32-bit
os2:
	$(MAKE) -f makefile.wat all \
	LINK="wlink libpath $(WATCOM)/lib386/os2;$(WATCOM)/lib386 format os2 lx"

#for DOS4G/W
dpmi:
	$(MAKE) -f makefile.wat all \
	LINK="wlink libpath $(WATCOM)/lib386/dos;$(WATCOM)/lib386 format os2 le op stub=wstub.exe"

#for Win32
win32:
	$(MAKE) -f makefile.wat all \
	LINK="wlink libpath $(WATCOM)/lib386/nt;$(WATCOM)/lib386 format windows nt runtime console"

SRCS =	crc.c mktmptbl.c main.c stage1.c keystuff.c stage2.c stage3.c exfunc.c\
	readhead.c writehead.c zipdecrypt.c

OBJS =	crc.obj mktmptbl.obj main.obj stage1.obj keystuff.obj stage2.obj stage3.obj exfunc.obj\
	readhead.obj writehead.obj zipdecrypt.obj

all: pkcrack.exe zipdecrypt.exe findkey.exe extract.exe makekey.exe

%.obj:	%.c
	$(CC) $<

pkcrack.exe: $(OBJS)
	$(LINK) name pkcrack.exe file main libfile crc.obj,mktmptbl.obj,stage1.obj,keystuff.obj,stage2.obj,stage3.obj,exfunc.obj,readhead.obj,writehead.obj,zipdecrypt.obj

findkey.exe: findkey.obj crc.obj stage3.obj keystuff.obj
	$(LINK) file findkey libfile crc.obj,stage3.obj,keystuff.obj,mktmptbl.obj

zipdecrypt.exe: zdmain.obj zipdecrypt.obj crc.obj keystuff.obj writehead.obj readhead.obj
	$(LINK) name zipdecrypt.exe file zdmain libfile zipdecrypt.obj,crc.obj,keystuff.obj,writehead.obj,readhead.obj

extract.exe: extract.obj exfunc.obj readhead.obj
	$(LINK) file extract libfile exfunc.obj,readhead.obj

makekey.exe: makekey.obj crc.obj keystuff.obj
	$(LINK) file makekey libfile crc.obj,keystuff.obj

clean:
	del *.obj *.exe

crc.c: crc.h

decrypt.c: crc.h pkcrack.h pkctypes.h keystuff.h mktmptbl.h

makekey.c: pkcrack.h keystuff.h crc.h

findkey.c: pkcrack.h stage3.h crc.h

keystuff.c: pkcrack.h crc.h keystuff.h

main.c: crc.h mktmptbl.h pkcrack.h stage1.h stage2.h stage3.h headers.h

stage1.c: crc.h mktmptbl.h pkcrack.h

stage2.c: crc.h keystuff.h mktmptbl.h pkcrack.h

stage3.c: crc.h keystuff.h pkcrack.h

zipdecrypt.c: crc.h keystuff.h pkcrack.h headers.h

extract.c: headers.h

exfunc.c: headers.h

readhead.c: headers.h

writehead.c: headers.h

mktmptbl.c: mktmptbl.h pkctypes.h
