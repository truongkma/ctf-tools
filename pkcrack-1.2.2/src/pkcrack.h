/* 
 * pkcrack.h
 *
 * This header file contains some constants used in the program and some
 * global variables from main.c
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: pkcrack.h,v 1.8 2002/11/02 15:12:06 lucifer Exp $
 *
 * $Log: pkcrack.h,v $
 * Revision 1.8  2002/11/02 15:12:06  lucifer
 * Integrated RElf's changes (with small mods) from fix2.zip
 *
 * Revision 1.8  2002/10/25 17:44:13  RElf
 * CONST, INVCONT, MAXDELTA, MSBMASK now defined here
 *
 * Revision 1.7  2002/01/21 19:41:29  lucifer
 * Change by RElf:
 * added MSB(x) macro definition
 *
 * Revision 1.6  1997/09/18 18:21:08  lucifer
 * moved global type definitions into "pkctypes.h" (D. Bragin)
 *
 * Revision 1.6  1996/09/06 11:48:23  bragin
 * moved global type definitions into "pkctypes.h"
 *
 * Revision 1.5  1996/08/21 17:37:20  conrad
 * memory for plain- and ciphertext is now allocated dynamically
 *
 * Revision 1.4  1996/08/13 13:20:27  conrad
 * Increased value of KEY2SPACE after several complaints. Now the array is
 * 32 MB...
 *
 * Revision 1.3  1996/06/23 10:28:48  lucifer
 * Modifications for DJGPP 2.0: DJGPP can't handle arrays larger than 16MB,
 * so key2i is now allocated dynamically.
 * DJGPP doesn't know about type ushort, either.
 *
 * Revision 1.2  1996/06/12  09:47:20  conrad
 * Release version
 *
 * Revision 1.1  1996/06/10 17:55:27  conrad
 * Initial revision
 *
 */

#ifndef _PKCRACK_H
#define _PKCRACK_H

#include "pkctypes.h"

#define	KEY2SPACE	(1<<23)	/* some more just for safety */

#define	KEY3(i)	(plaintext[(i)]^ciphertext[(i)])

#define MSB(x)          (((x)>>24)&0xFF)

extern byte	*plaintext, *ciphertext;
extern uword	*key2i;
extern int	numKey2s, bestOffset;

#define	CONST		0x08088405U	/* 134775813 */
#define	INVCONST	0xd94fa8cdU	/* CONST^{-1} */

#define MAXDELTA        (0x00FFFFFFU+0xFFU)
#define MSBMASK         0xFF000000U

#endif /* _PKCRACK_H */
