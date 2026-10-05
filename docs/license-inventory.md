# 文件级许可清单(2026-10-06)

> 任务:Task 12(M1)。事实源:T8 调研报告 `reports/2026-10-06-toaruos-survey.md`、根 `NOTICE`、`REUSE.toml`。
> 口径:按 spec §6 风险 2,**M1 只出清单,不宣布**"纯 MIT"。

## 1. 自有内容

| 范围 | 许可 | 来源 |
|---|---|---|
| 本仓全部自有文件(除下述许可/通告文件) | MIT | `REUSE.toml` 全仓 `path = ["**"]` 映射;许可全文 `LICENSES/MIT.txt` |
| `LICENSE`、`NOTICE`、`LICENSES/**` 本身 | CC0-1.0 | `REUSE.toml` 第二条 annotation(REUSE 惯例:许可文本不主张版权) |

## 2. 上游底座

底座:`base/toaruos`,锁定 `e77143fd14391d880c3ee11c1524252cdcbfd225`(T8 报告 §1)。

| 组件 | 位置 | 许可 | 处置 | 来源 |
|---|---|---|---|---|
| 底座一方代码(内核/libc/lib/apps/boot) | `base/toaruos/` | UIUC/NCSA(BSD 类宽松许可) | submodule 内 `LICENSE` 原样保留,不重标注 | T8 报告 §2;底座内 `LICENSE` |
| bim(轻量编辑器) | 子模块 `bim`,锁定 `8ece591f` | ISC 类;许可见其上游 LICENSE | 随底座原样保留 | T8 报告 §2 表格 |
| kuroko(解释器) | 子模块 `kuroko`,锁定 `50e45b4a` | MIT,**含第二版权人**(Robert Nystrom,2015 部分) | 随底座原样保留,保留双方版权 | T8 报告 §2 表格 |
| binutils-gdb | 子模块 `util/binutils-gdb`,锁定 `facad00e` | GPL-3(+ LGPL 部分),构建期工具链 | 仅构建期使用;产物(交叉工具链二进制)不随镜像分发。**"不进入运行时镜像的许可义务范围"——待法务口径确认,非定论** | T8 报告 §2 表格、§spec 影响 2 |
| gcc | 子模块 `util/gcc`,锁定 `66860610` | GPL-3,构建期工具链 | 同上:仅构建期使用。**"不进入运行时镜像的许可义务范围"——待法务口径确认,非定论** | T8 报告 §2 表格、§spec 影响 2 |

注:四个子模块 SHA 见 T8 报告 §风险 2;子模块许可文件读自各自上游浅克隆(与主仓锁定一致)。

## 3. 资源缺口(追踪项)

| 资源 | 位置 | 问题 | 对策 |
|---|---|---|---|
| DejaVu 字体(8 个 .ttf) | `base/toaruos/base/usr/share/fonts/truetype/dejavu/` | 上游仓库内**无**独立许可文件(T8 报告 §2 表格、§风险 3) | 追踪项:①向上游提 issue 询问/索取许可文件;或 ②从 DejaVu 官方核对该版本许可(DejaVu 项目许可为 Bitstream Vera 衍生的宽松许可,具体版本以官方核对为准)。核实后在 NOTICE/本清单补条目 |

## 4. 结论

**宣布"纯 MIT"尚缺,暂不宣布**(spec §6 风险 2 口径:M1 只出清单):

1. **DejaVu 字体许可核实**(§3 缺口);
2. **GPL 构建期边界口径**:binutils-gdb / gcc "仅构建期、不进入运行时镜像许可义务范围"的表述**待法务口径确认**(§2);
3. (可选)后续引入的一切第三方组件,逐个清算登记至本清单。
