# EtherOS 顶层 Makefile:check 为结构校验;build 转发至 ToaruOS 底座(base/toaruos)
.DEFAULT_GOAL := build
.PHONY: check build clean

check:
	bash tools/check-skeleton.sh

build: check
	$(MAKE) -C base/toaruos

clean:
	@echo "[EtherOS] nothing to clean (M0)"
