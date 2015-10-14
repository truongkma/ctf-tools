/* 
 * stage3.h
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: stage3.h,v 1.5 2002/11/02 15:12:06 lucifer Exp $
 *
 * $Log: stage3.h,v $
 * Revision 1.5  2002/11/02 15:12:06  lucifer
 * Integrated RElf's changes (with small mods) from fix2.zip
 *
 * Revision 1.5  2002/10/25 17:55:37  RElf
 * initStage3Tab() removed
 *
 * Revision 1.4  1997/09/18 18:35:59  lucifer
 * Added _STAGE3_H and pkctypes.h
 *
 * Revision 1.3  1996/06/23 10:40:49  lucifer
 * Added support for restarting search
 * ,
 *
 * Revision 1.2  1996/06/12 09:47:29  conrad
 * Release version
 *
 * Revision 1.1  1996/06/10 18:08:59  conrad
 * Initial revision
 *
 */

#ifndef _STAGE3_H
#define _STAGE3_H

#include "pkctypes.h"

extern void findPwd( uword key0, uword key1, uword key2 );
extern void findLongPwd( uword key0, uword key1, uword key2, int pwdLen, uword initBytes );

#endif /* _STAGE3_H */
