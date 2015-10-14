/*
 * crc.c
 *
 * This file contains functions for calculating CRC-32 checksums.
 * The CRC-polynomial used is defined in crc.h
 * A lookup-table is used, which has to be initialized first.
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: crc.c,v 1.3 1997/09/18 18:07:24 lucifer Release1_2_1 $
 *
 * $Log: crc.c,v $
 * Revision 1.3  1997/09/18 18:07:24  lucifer
 * Added comment
 *
 * Revision 1.2  1996/06/12 09:37:05  conrad
 * Release version
 *
 * Revision 1.1  1996/06/10 17:31:10  conrad
 * Initial revision
 *
 */

static char RCSID[]="$Id: crc.c,v 1.3 1997/09/18 18:07:24 lucifer Release1_2_1 $";

#include "crc.h"

crcword crctab[256], crcinvtab[256];

void mkCrcTab( )
{
unsigned int i, j, c;

    for( i = 0; i < 256; i++ )
    {
	c = i;
	for( j = 0; j < 8; j++ )
	    if( c&1 )
		c = (c>>1) ^ CRCPOLY;
	    else
		c = (c>>1);
	crctab[i] = c;
	crcinvtab[c>>24] = (c<<8) ^ i;
    }
}

