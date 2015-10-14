/* 
 * mktmptbl.c
 *
 * This file contains a function for initializing a lookup-table that
 * is used for finding "temp" values for a given "key3" (refer to the paper if
 * you want to know what "temp" and "key3" are).
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: mktmptbl.c,v 1.9 2002/11/02 15:12:06 lucifer Exp $
 *
 * $Log: mktmptbl.c,v $
 * Revision 1.9  2002/11/02 15:12:06  lucifer
 * Integrated RElf's changes (with small mods) from fix2.zip
 *
 * Revision 1.9 2002/10/25 17:41:24 RElf
 * Joint with mulTab data/routines
 *
 * Revision 1.8  2002/01/31 16:24:22  lucifer
 * Reorganized invTempTable
 *
 * Revision 1.7  2002/01/30 15:27:10  lucifer
 * Integrated changes by RElf
 *
 * Revision 1.6  1998/05/08 16:55:49  lucifer
 * Added creation of inverted tempTable
 *
 * Revision 1.5.2.1  2002/01/21 19:38:25  lucifer
 * Changes by RElf:
 * Reorganized loop, changed type of temp, commented useless check
 *
 * Revision 1.5  1997/09/18 18:18:39  lucifer
 * Added comment, moved DJGPP-specific #defines into mktmptbl.h
 *
 * Revision 1.4  1996/08/13 13:19:19  conrad
 * Changed name to support OS with short filenames... :-/
 *
 * Revision 1.3  1996/06/23 12:34:08  lucifer
 * #defined ushort for DJGPP
 *
 */

static char RCSID[]="$Id: mktmptbl.c,v 1.9 2002/11/02 15:12:06 lucifer Exp $";

#include <stdio.h>
#include "mktmptbl.h"

ushort	tempTable[256][64];
static int numEntries[256];

byte	invTempTable[256][64][INVTEMP_NUM];
ushort	invEntries[256][64];

void preCompTemp( )
{
uword	temp, key3;

    memset(numEntries, 0, sizeof(numEntries));
    memset(invEntries, 0, sizeof(invEntries));

    temp = 0x10000;
    do{
	key3 = (((temp|2) * (temp|3))>>8)&0xff;
	tempTable[key3][numEntries[key3]++] = temp;
/*	if( numEntries[key3] > 64 )
	    fprintf( stderr, "Warning! Lookup-table corrupted!\n" ); */
    }while( temp-=4 );

    // invTempTable[key3][(anotherKey2Value>>10)&63] is to be used for finding
    // all k so that
    // tempTable[key3][k] & 0xfc00 == anotherKey2Value & 0xfc00
    for (key3 = 0; key3 < 256; key3++) {
	for (temp = 0; temp < 64; temp++) {
	    invTempTable[key3][(tempTable[key3][temp]>>10)&63]
			[invEntries[key3][(tempTable[key3][temp]>>10)&63]++] = temp;
/*	    if (invEntries[key3][(tempTable[key3][temp]>>10)&63] > INVTEMP_NUM){
		fprintf(stderr,"inventries != 1: %d\n", invEntries[key3][temp]);
		exit(-1);
	    } */
	}
    }
}

uword	mulTab[256];
byte	mTab2[256][2];
int	mTab2Counter[256];

void initMulTab( )
{
uword	i, prod;
byte	j;

    memset(mTab2Counter, 0, sizeof(mTab2Counter));
    for( i = 0, prod = 0; i < 256; i++, prod+=INVCONST )
    {
	mulTab[i] = prod;
	j = MSB(prod);
	mTab2[j][mTab2Counter[j]++] = i;
    }
}
