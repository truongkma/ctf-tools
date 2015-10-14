/* 
 * pkctypes.h
 *
 * This header contains global type definitions for different
 * platforms.
 *
 * (C) 1996 by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: pkctypes.h,v 1.2 1997/09/18 18:22:10 lucifer Release1_2_1 $
 *
 * $Log: pkctypes.h,v $
 * Revision 1.2  1997/09/18 18:22:10  lucifer
 * Moved some more stuff in here
 *
 * Revision 1.1  1996/09/22  09:26:34  lucifer
 * Initial revision
 *
 */

#ifndef _PKCTYPES_H
#define _PKCTYPES_H

#ifndef _WIN32

#include <sys/types.h>

#ifdef __DJGPP__
#define	ushort	unsigned short
#endif /* DJGPP */

#endif /* !WIN32 */

#ifndef byte
#define	byte	unsigned char
#endif


#ifndef uword
#define uword	unsigned int	/* 32 bit wide */
#endif

#ifndef ushort
#define	ushort	unsigned short	/* 16 bit wide */
#endif

#endif /* _PKCTYPES_H */
