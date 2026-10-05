# EtherOS M0 空构建桩:M1 起由底座真实构建接管 build 目标
.PHONY: check build clean

check:
	bash tools/check-skeleton.sh

build: check
	@echo "[EtherOS] M0 空构建:结构校验通过,无编译目标(M1 接入 ToaruOS 底座)"

clean:
	@echo "[EtherOS] nothing to clean (M0)"
