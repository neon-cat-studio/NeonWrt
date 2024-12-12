include mkinc.mak
CFLAGS+=-Iinclude -fPIC
all: libstemmer.so libstemmer.a stemwords
libstemmer.so: $(snowball_sources:.c=.o)
	$(CC) $(CFLAGS) -shared $(LDFLAGS) -Wl,-soname,$@.0d -o $@.0d.0.0 $^
	ln -s $@.0d.0.0 $@.0d
	ln -s $@.0d.0.0 $@
libstemmer.a: $(snowball_sources:.c=.o)
	$(AR) -crs $@ $^
stemwords: examples/stemwords.o libstemmer.so
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^
clean:
	rm -f stemwords libstemmer.so* libstemmer.a *.o src_c/*.o runtime/*.o libstemmer/*.o
