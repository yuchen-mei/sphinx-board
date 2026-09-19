# Legacy V1 — 第一版Sphinx板归档

**本分支是第一版已使用板子的历史快照，不是当前2.6.5原理图，也不是新版PCB。** 当前设计请转到[main](https://github.com/yuchen-mei/sphinx-board/tree/main)。

## 归档身份

- 分支：`legacy/v1`
- 固定标签：`legacy-v1-archive`
- 归档日期：2026-09-18；这是保存日期，不代表原板设计或制造日期。
- 架构：外部电源直接供0V75 / 1V8的无源转接板，包含socket、接口、去耦与手动复位；没有新版板载电源调节和硬件保护控制链。
- 这是用户报告已用HP8133A时钟源正常工作的旧板基线；该使用经验不等于全部电气极限已经认证。

## 文件

打开 [board/sphinx_board.kicad_pro](board/sphinx_board.kicad_pro)。

- [原始原理图](board/sphinx_board.kicad_sch)
- [原始PCB](board/sphinx_board.kicad_pcb)
- [原始CSV BOM](board/sphinx_board.csv)
- [历史BOM工作簿](board/Sphinx%20BOM.xlsx)
- [历史更新版BOM工作簿](board/sphinx_board%20BOM%20updated.xlsx)

以上六个文件按原件逐字节保存，SHA-256见[ARCHIVE_MANIFEST.json](ARCHIVE_MANIFEST.json)。两个BOM工作簿保留原文件名，不推断哪一份代表最终实装。未补造Gerber或制造放行记录。

原项目引用旧电脑的`my_symbols` / `my_footprints`库；原理图和PCB内嵌的符号/封装随原文件保留，外部自定义库目录未在来源中找到。查看原板可使用内嵌对象；若重新编辑并从库更新，应先恢复或明确重建这些历史库，不要自动套用新版socket封装。

## 维护约定

本分支用于追溯，避免修改或合并到main。需要修改旧板时，从`legacy-v1-archive`创建新的工作分支。`main`与本分支使用独立提交历史，避免旧PCB混入当前原理图项目。

原始工作区文件仍保留；该归档未改动原板的布线、网络、元件值或机械数据。
