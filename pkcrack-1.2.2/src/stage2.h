/* 
 * stage2.h
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: stage2.h,v 1.6 2002/11/02 15:12:06 lucifer Exp $
 *
 * $Log: stage2.h,v $
 * Revision 1.6  2002/11/02 15:12:06  lucifer
 * Integrated RElf's changes (with small mods) from fix2.zip
 *
 * Revision 1.6  2002/10/25 17:54:38  RElf
 * initMulTab() moved to mktmptbl.h
 *
 * Revision 1.5  2002/01/21 19:45:38  lucifer
 * Change by RElf:
 * added got_keys
 *
 * Revision 1.4  1997/09/18 18:35:27  lucifer
 * Added _STAGE2_H
 *
 * Revision 1.3  1996/08/13 13:24:18  conrad
 * expanded arg list for buildKey2Lists()
 *
 * Revision 1.2  1996/06/12 09:47:26  conrad
 * Release version
 *
 * Revision 1.1  1996/06/10 18:07:33  conrad
 * Initial revision
 *
 */

#ifndef _STAGE2_H
#define _STAGE2_H

#include "pkctypes.h"

extern void buildKey2Lists( uword aKey2_13, int testBytes, int minOffset );

extern uword	loesung0, loesung1, loesung2, got_keys;

#endif /* _STAGE2_H */
