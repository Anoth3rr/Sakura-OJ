CXX?=g++
CXXFLAGS?=-Wall -Os -g

ifneq ($(NDEBUG),)
CXXFLAGS += -DNDEBUG
endif

ifeq ($(DESTDIR),)
PREFIX?=/usr/local
else
PREFIX?=/usr
endif

.SUFFIXES:

.PHONY: all clean install cog

all: ljudge linteractive lworkflow

ljudge: ljudge.o sha1.o fs.o term.o
	$(CXX) -o $@ $(LDFLAGS) -fopenmp $^ -pthread -ldl

linteractive: linteractive.o sha1.o fs.o term.o
	$(CXX) -o $@ $(LDFLAGS) -fopenmp $^ -pthread -ldl

lworkflow: lworkflow.cc deps/picojson/picojson.h
	$(CXX) -std=c++17 $(CXXFLAGS) $(LDFLAGS) -o $@ lworkflow.cc -pthread

%.o: %.cc
	$(CXX) -pthread -std=c++0x -fopenmp -c -o $@ $(CXXFLAGS) $<

clean:
	-rm -f *.o **/*.o ljudge linteractive lworkflow

install: ljudge linteractive lworkflow
	install -D -m0755 -oroot -groot -s ljudge $(DESTDIR)$(PREFIX)/bin/ljudge
	install -D -m0755 -oroot -groot -s linteractive $(DESTDIR)$(PREFIX)/bin/linteractive
	install -D -m0755 -oroot -groot -s lworkflow $(DESTDIR)$(PREFIX)/bin/lworkflow
ifneq ($(DESTDIR),)
	mkdir -p $(DESTDIR)/etc/
	cp -a ../etc/ljudge $(DESTDIR)/etc/
endif

cog: ljudge.cc
	cog.py -r $^
#make && sudo make install
