

default:
	@echo 'Global makefile'
	@echo
	@echo 'Usage:'
	@echo
	@echo '    make install    install the packages'
	@echo '    make clean      cleanup IDL generated file'
	@echo '    make build      generate code from IDL'
	@echo

install:
	make -C client-2.x/ install
	make -C server-3.x/ install

clean:
	make -C client-2.x/ clean
	make -C server-3.x/ clean

build:
	make -C client-2.x/ build
	make -C server-3.x/ build
