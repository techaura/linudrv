CC=gcc
MODFLAGS:= -O3 -Wall -DLINUX
module.o: module.c
$(CC) $(MODFLAGS) -c module.c