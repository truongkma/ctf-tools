/* 
 * mktmptbl.h
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: mktmptbl.h,v 1.8 2002/11/02 15:12:06 lucifer Exp $
 *
 * $Log: mktmptbl.h,v $
 * Revision 1.8  2002/11/02 15:12:06  lucifer
 * Integrated RElf's changes (with small mods) from fix2.zip
 *
 * Revision 1.8 2002/10/25 17:41:24 RElf
 * Joint with mulTab routines
 *
 * Revision 1.7  2002/01/31 16:24:22  lucifer
 * Reorganized invTempTable
 *
 * Revision 1.6  1998/05/08 16:55:49  lucifer
 * Added creation of inverted tempTable
 *
 * Revision 1.5  1997/09/18 18:19:46  lucifer
 * Added _MKTMPTBL_H & pkctypes.h
 *
 * Revision 1.4  1996/08/13 13:19:48  conrad
 * Changed name to support OS with short filenames... :-/
 *
 * Revision 1.3  1996/06/23 12:34:20  lucifer
 * #defined ushort for DJGPP
 *
 */

#ifndef _MKTMPTBL_H
#define _MKTMPTBL_H

#include "pkctypes.h"
#include "pkcrack.h"

#define INVTEMP_NUM     5

extern ushort tempTable[256][64];
extern void   preCompTemp( void );
extern byte   invTempTable[256][64][INVTEMP_NUM];
extern ushort invEntries[256][64];

#define	MULT(x)		((mulTab[((x)>>24)&0xff]<<24) + \
			 (mulTab[((x)>>16)&0xff]<<16) + \
			 (mulTab[((x)>> 8)&0xff]<< 8) + \
			 (mulTab[((x)    )&0xff]    ))

extern uword	mulTab[256];
extern byte	mTab2[256][2];
extern int	mTab2Counter[256];
extern void initMulTab();

#endif /* _MKTMPTBL_H */
