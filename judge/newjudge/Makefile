.PHONY: all judge sandbox clean

all: judge sandbox

judge:
	$(MAKE) -C ljudge/src

sandbox:
	NDEBUG=1 $(MAKE) -C lrun
	$(MAKE) -C lrun/utils/mirrorfs

clean:
	$(MAKE) -C ljudge/src clean
	$(MAKE) -C lrun clean
	$(MAKE) -C lrun/utils/mirrorfs clean
