from Crypto.Random import random
import challenge21
import time

t = int(time.time())
t += random.randint(40, 1000)
seed = int(t)
print(seed)
rng = challenge21.MT19937(seed)
x = rng.uint32()
print(x)

t += random.randint(40, 1000)
for i in range(2000):
    k = t - i
    rng2 = challenge21.MT19937(k)
    y = rng2.uint32()
    if x == y:
        print(k)
