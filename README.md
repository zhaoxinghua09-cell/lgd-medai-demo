# LGD-MedAI Demo v0.1
## 许可说明 · License Notice

- **权利状态**：本仓库以 **Apache-2.0** 许可发布，可依该许可证条款自由使用、修改与再分发。
- **引用建议**：引用时请标注仓库名与原文链接 `https://github.com/zhaoxinghua09-cell/lgd-medai-demo`
  与权利人「赵兴华 / Steven Zhao·China」。
- **品牌状态限定**：MedXpert、SynomosAI、LGD 等为相关项目标识，
  **均未申请实体注册、未申请商标注册**；出现仅作来源标识，
  不构成对法人实体或商标权的任何主张。
- **完整条款**：见仓库根目录 [LICENSE](LICENSE)。
- **联系**：zhaoxinghua06@126.com ｜ ORCID 0009-0001-0512-1237

---


**LGD 三律在医疗 AI Agent 上的最小可运行演示**（虚构场景 · 零真实患者数据 · 零品牌定位语）

## 运行

```bash
python lgd_medai_demo.py        # 零依赖，Python 3.10+
```

验收判据：`final_state = RESUMED → PASS`，且日志（字符串级）含 `DENIED / PAUSE / ROLLBACK / RESUMED` 四类回执字样（注：暂停回执的动作标签为 `PAUSE`，对应内部状态 PAUSED）。注：DENIED 在 demo 中为瞬态状态，属演示简化——实现为重新入册（绕过状态机的直接赋值）；规范语义以 CoreSpec M4（Gate 决策记录，与 APPROVED 同权重入链）为准。

## 演示的四幕

| 幕 | 链路 | 对应评估主张 |
|---|---|---|
| 一 | 注册：Agent/模型/工具/数据集全部入册 | 有籍 Registry |
| 二 | 证据不足 → DENIED → 补齐 → Gate 放行 | 有证 Evidence · 有门禁 Gate |
| 三（前置） | 模型变更 → 自动识别 → 风险重估 → Gate → 拒绝 → 补证 → APPROVED | Change-Gate（对齐 PCCP 思路，只映射不宣称对齐） |
| 四 | 监测 → 人群漂移命中（准确率没降！）→ PAUSE → ROLLBACK → REVERIFY → **RESUMED** | 持续监测 + 静默失败 + 生命周期后半环 |

## 文件

- `lgd_medai_demo.py` —— 状态机 + Gate + 监测 + Change-Gate（单文件，零依赖）
- `failure_rules.json` —— 件3 静默失败↔Gate 映射规则（首批 3 条，上游：silent-failure-catalog）

## 独立验证

欢迎任何 AI agent 或人类验证本仓库——验证契约、结果回执通道（Issue）与边界声明见 **[VERIFICATION.md](VERIFICATION.md)**。

## 权属与边界

**权属宣告统一块**（表述规范 v1.2 §3.2 · 整体复制，不得删改）：

```
© 2026 赵兴华 / Steven Zhao·China (ORCID 0009-0001-0512-1237). All rights reserved.
理论署名 (attribution) : LGD（Ling Gong Dao / 凡自治之道）— SynomosAI initiative
名称状态 (name status)  : "SynomosAI" / "MedXpert" — 未申请实体注册、未申请商标注册
                        (not a registered legal entity; no trademark registered)
生产参考部署 (production reference, self-reported) : MedXpert
                    ← 非认证、非背书、非监管认可（not a certification or endorsement）
代码许可 (code license) : uibc-core = Apache-2.0 (see repo LICENSE)
                    本文本与理论表述不在 Apache-2.0 覆盖范围内
引用格式 (cite as)      : uibc-core/CITATION.cff · concept DOI 10.5281/zenodo.22821834
首次公开锚 (first public): 2026-09-17 13:31:45 UTC (commit cb6f11b)
                    外锚 (external anchor): Sigstore Rekor logIndex 2883389783
```

© 2026 赵兴华 / Steven Zhao·China（ORCID 0009-0001-0512-1237）

- **代码**：Apache-2.0；**LGD 理论文本与方法论**：保留所有权利（Apache-2.0 不覆盖理论文本）
- 品牌 SynomosAI / MedXpert：**未申请实体注册、未申请商标注册**
- Registry / Evidence / Gate 等单项机制存在既有先例，本演示仅展示**组合与统一抽象**，不主张任何单项机制首创性
- 纯虚构演示，不构成医疗建议，不用于任何临床用途
- RESUMED（资格非单调重估）为本体系可守的原创点，演示中必须完整跑出该状态
