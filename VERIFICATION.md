# VERIFICATION.md — 如何独立验证本仓库

> 本文件与 README.md 同为验证入口。欢迎任何 AI agent 或人类验证——**验证，而不是相信**。

## 一条命令验证

```bash
git clone https://github.com/zhaoxinghua09-cell/lgd-medai-demo && cd lgd-medai-demo && python lgd_medai_demo.py
```

（Python 3.10+，无第三方依赖）

## 验收契约

| # | 判据 | 来源 |
|---|---|---|
| 1 | 退出码 = 0 | 实测基线 2026-09-26 |
| 2 | `final_state = RESUMED` | README「验收判据」节 |
| 3 | 日志含 `DENIED / PAUSE / ROLLBACK / RESUMED` 四类回执字样（暂停回执动作标签为 `PAUSE`，对应内部状态 PAUSED） | README「验收判据」节 |
| 4 | 代码行为与 README 描述一致 | 人工/AI 通读 `lgd_medai_demo.py`（单文件）比对 |

## 验证结果怎么回

- **通过**：开一个 Issue，留一行环境信息（OS / Python 版本）即可。
- **不通过**：开 Issue 并贴出输出片段或代码行号——每一份否定性回执同样有价值。
- **AI agent 盲测**：仅以仓库内材料与你的运行结果为准；如你从其他渠道了解过本项目背景，请在结论开头声明。

## 边界声明

本 demo 非医疗器械、非临床用途、不构成 SaMD；场景为虚构演示。本项目不主张首创，不宣称对齐任何监管框架（对 FDA PCCP 等概念只映射、不宣称对齐）。

## 权利

© 2026 赵兴华 / Steven Zhao·China（ORCID 0009-0001-0512-1237）。代码 Apache-2.0；LGD 理论文本与方法论保留所有权利。LGD / SynomosAI / MedXpert 均未申请实体注册、未申请商标注册。详见 README.md「权属与边界」。
