#ifndef _DEBUG_H_
#define _DEBUG_H_

#ifdef DEBUG

#define checkKey1list(array,offset) if (!_checkKey1list(array, offset)) { return; }
extern int _checkKey1list(uword *array, int offset);

#define checkRecursion1(array,offset,i) if (!_checkRecursion1(array, offset, i)) { return; }
extern int _checkRecursion1(uword *array, int offset, int i);

#define checkKey2list(array,offset) if (!_checkKey2list(array, offset)) { return; }
extern int _checkKey2list(uword *array, int offset);

extern void prepareDebug(int i);
extern void checkKey2(int i);

#else /* ifdef DEBUG */

#define checkKey1list(array,offset)
#define checkRecursion1(array,offset,i)
#define checkKey2list(array,offset)

#endif /* ifdef DEBUG */

#endif /* _DEBUG_H_ */

