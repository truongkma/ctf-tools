/* 
 * crc.h
 *
 * This file contains macros for computing CRC-checksums using a lookup-table
 * which has to be initialized using a function in crc.c
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: crc.h,v 1.3 1997/09/18 18:12:31 lucifer Release1_2_1 $
 *
 * $Log: crc.h,v $
 * Revision 1.3  1997/09/18 18:12:31  lucifer
 * Added _CRC_H
 *
 * Revision 1.2  1996/06/12 09:38:17  conrad
 * Release version
 *
 * Revision 1.1  1996/06/10 17:34:40  conrad
 * Initial revision
 *
 */

#ifndef _CRC_H
#define _CRC_H

#define	crcword		unsigned int

extern void mkCrcTab( );

extern crcword	crctab[256], crcinvtab[256];

#define CRCPOLY	0xedb88320

#define CRC32(x,c)	(((x)>>8)^crctab[((x)^(c))&0xff])
#define	INVCRC32(x,c)	(((x)<<8)^crcinvtab[((x)>>24)&0xff]^((c)&0xff))

#endif /* _CRC_H */
