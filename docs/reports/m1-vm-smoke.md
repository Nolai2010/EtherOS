# M1 VM Smoke 证据报告（T11 / T14-A6）

状态：**通过**。本文档是 M1 独立验收中"入库报告"一项的存档，描述 CI 中 vm-smoke job 的实际运行方式与取得的证据。

## CI 结论

CI run [37387961480](https://github.com/Nolai2010/EtherOS/actions/runs/37387961480)（commit `1318a54`）三个 job 全绿：

| Job | 结论 | 耗时 |
|---|---|---|
| etherkit-consistency | ✓ | 6s |
| build | ✓ | 2m25s |
| vm-smoke | ✓ | 24s |

build job 产出 image.iso / misaka-kernel / ramdisk.igz，经 artifact `etheros-boot-artifacts` 传递给 vm-smoke；vm-smoke 一次性通过，未消耗修复轮次。

## vm-smoke 跑法（headless）

跑法忠实上游 `base/toaruos/build/x86_64.mk` 的 `shell` 目标（官方 headless 串口跑法）：

- `-M q35` + `-fw_cfg name=opt/org.toaruos.bootmode,string=headless` + `-fw_cfg name=opt/org.toaruos.gettyargs,string="-a local /dev/ttyS1 115200 ${TERM}"`
- bootloader 的 `detect_qemu`（`base/toaruos/boot/qemu.c:41`）经 fw_cfg 读取 bootmode，跳过启动菜单并以 `start=--headless` 启动；`base/toaruos/base/etc/startup.d/99_runstart.sh:16` 据此执行 `/bin/getty ${GETTY_ARGS}`，getty 落在 `/dev/ttyS1`（COM2）。
- 双串口：COM1 接 `serial-com1.log`（内核 0x3F8 早期日志），COM2 接 `serial-com2.log`（getty/login）。
- 未加 `-vga none`（bootloader/fbterm 依赖 VGA 设备），使用 `-display none` 实现 headless。
- 断言方式：不用 autologin 快捷路径（上游 `-a local` 会让 login 走 `-f` 路径跳过提示输出），而是等待交互式 getty → login 打印 `"%s login: "`（`base/toaruos/apps/login.c:86`），hostname 取自 `base/toaruos/base/etc/hostname` = `livecd`。job 轮询 `serial-com2.log`（每 5s 一次，上限 120s），实际第 1 轮（约 5s）即命中，断言输出 `BOOT EVIDENCE OK: userspace login reached on serial (COM2)`。

## serial.log 摘录（CI 日志原文，`cat -v` 转义可见）

```
---- serial-com1.log (COM1 early log, head 100) ----
(空,0 字节)
---- serial-com2.log (COM2 getty/login, head 100) ----
^[[s^[[1000;1000H^[[6n^[[ulivecd login:
```

- `livecd login:` 即 `base/toaruos/apps/login.c:86` 的输出，hostname 来自 `base/toaruos/base/etc/hostname`（`livecd`）；前置转义序列为 `ttysize -q` 的终端尺寸查询，均为真实 guest 输出。

## QMP screendump

命中断言后，job 通过 QMP（`qmp_capabilities` + `screendump`）导出当时的 VGA 帧缓冲画面为 `screen.ppm`（1920x1080），作为 fbterm 内核控制台画面的辅助证据。screendump 仅辅助取证，不参与通过/失败判定。

## 证据 artifact

完整证据三件套（serial-com1.log / serial-com2.log / screen.ppm）存于该 run 的 artifact **`vm-smoke-evidence`**（artifact ID 11380158734）。

## COM1 早期日志为空的说明

COM1 serial-com1.log 为 0 字节，这是事实而非故障：内核 banner 经 `dprintf` → `write_console`（`base/toaruos/kernel/vfs/console.c`）进入 framebuffer 通道（fbterm），不走 COM1；走 COM1 的 `_early_log_write`（`base/toaruos/kernel/arch/x86_64/main.c`）在正常启动路径的早期窗口内几乎无 printf 调用，且 fbterm 初始化后输出切向 framebuffer。因此内核侧串口证据由以下两项承担：

1. COM2 用户态 login banner —— 证明内核已跑通 ramdisk / 驱动 / init 全链路；
2. QMP screendump —— fbterm 内核控制台画面。

报告如实记录，未编造内核 banner。
