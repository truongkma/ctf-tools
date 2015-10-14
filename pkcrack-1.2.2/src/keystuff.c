/* 
 * keystuff.c
 *
 * This file contains functions for initializing and updating the
 * internal state of the PkZip cipher.
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: keystuff.c,v 1.5 2002/11/02 15:12:06 lucifer Exp $
 *
 * $Log: keystuff.c,v $
 * Revision 1.5  2002/11/02 15:12:06  lucifer
 * Integrated RElf's changes (with small mods) from fix2.zip
 *
 * Revision 1.5  2005/10/25 18:02:49  RElf
 * symbolic constants are used
 *
 * Revision 1.4  1997/09/18 18:16:08  lucifer
 * Added comment and new header file
 *
 * Revision 1.3  1996/06/12 09:46:51  conrad
 * Release version
 *
 * Revision 1.2  1996/06/11 10:27:57  conrad
 * added function cUpdateKeys() for decrypting stuff
 *
 * Revision 1.1  1996/06/10 17:46:07  conrad
 * Initial revision
 *
 */

static char RCSID[]="$Id: keystuff.c,v 1.5 2002/11/02 15:12:06 lucifer Exp $";

#include "pkctypes.h"
#include "keystuff.h"
#include "pkcrack.h"
#include "crc.h"

uword	key0, key1, key2;
ushort	temp;
byte	key3;

void initkeys()
{
    key0 = KEY0INIT;
    key1 = KEY1INIT;
    key2 = KEY2INIT;
}

void updateKeys( byte plainbyte )
{
    key0 = CRC32( key0, plainbyte );
    key1 = (key1 + (key0&0xff))*CONST + 1;
    key2 = CRC32( key2, MSB(key1) );
    temp = (key2&0xffff) | 3;
    key3 = ((temp * (temp^1))>>8)&0xff;
}

byte cUpdateKeys( byte cipherbyte )
{
byte plainbyte;

    temp = (key2&0xffff) | 3;
    key3 = ((temp * (temp^1))>>8)&0xff;
    plainbyte = cipherbyte^key3;
    updateKeys( plainbyte );

    return plainbyte;
}

