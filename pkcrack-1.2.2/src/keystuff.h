/* 
 * keystuff.h
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: keystuff.h,v 1.6 2002/11/02 15:12:06 lucifer Exp $
 *
 * $Log: keystuff.h,v $
 * Revision 1.6  2002/11/02 15:12:06  lucifer
 * Integrated RElf's changes (with small mods) from fix2.zip
 *
 * Revision 1.6  2002/10/25 16:24:55  RElf
 * introduced KEY?INIT constants
 *
 * Revision 1.5  1997/09/18 18:16:31  lucifer
 * *** empty log message ***
 *
 * Revision 1.4  1996/08/13 13:15:39  conrad
 * added #include <sys/types> for ushort
 *
 * Revision 1.3  1996/06/12 09:47:06  conrad
 * Release version
 *
 * Revision 1.2  1996/06/11 10:28:15  conrad
 * added function cUpdateKeys() for decrypting stuff
 *
 * Revision 1.1  1996/06/10 17:47:22  conrad
 * Initial revision
 *
 */

#ifndef _KEYSTUFF_H
#define _KEYSTUFF_H

#include "pkctypes.h"

#define KEY0INIT 0x12345678u
#define KEY1INIT 0x23456789u
#define KEY2INIT 0x34567890u

extern uword 	key0, key1, key2;
extern ushort	temp;
extern byte	key3;

extern void initkeys();
extern void updateKeys( byte plainbyte );
extern byte cUpdateKeys( byte cipherbyte );

#endif /* _KEYSTUFF_H */
