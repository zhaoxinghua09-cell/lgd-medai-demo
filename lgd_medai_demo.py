#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LGD-MedAI Demo v0.1 —— LGD 三律在医疗 AI Agent 上的最小可运行演示
====================================================================

全生命周期链路（单命令可跑，零依赖）:
    注册(REGISTER) → 证据(EVIDENCE) → 门禁(GATE) → 执行(ACTIVE)
    → 监测(MONITOR) → 异常(ANOMALY) → 暂停(PAUSE) → 回退(ROLLBACK)
    → 重新验证(REVERIFY) → 恢复(RESUMED)

另含 Change-Gate 子链:
    模型变更 → 自动识别 → 风险重估 → 证据检查 → Gate → 发布/拒绝/回滚

────────────────────────────────────────────────────────────────────
权属宣告（Rights Notice）
© 2026 赵兴华 / Steven Zhao·China（ORCID 0009-0001-0512-1237）
· 本文件代码：Apache-2.0 许可
· LGD 理论文本与方法论：保留所有权利（Apache-2.0 不覆盖理论文本）
· 品牌 SynomosAI / MedXpert：未申请实体注册、未申请商标注册
· 本演示为虚构场景，不含任何真实患者数据，不构成医疗建议
· Registry / Evidence / Gate 等单项机制存在既有先例；本演示仅展示
  「组合与统一抽象」，不主张任何单项机制的首创性
────────────────────────────────────────────────────────────────────
"""
import json
import hashlib
import time
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(HERE, "failure_rules.json")


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


class Evidence:
    """证据件：每次关键动作的依据（虚构测试结果/审计记录）"""

    def __init__(self, kind: str, ref: str, content: str):
        self.kind = kind          # bench_test / clinical_review / version_manifest ...
        self.ref = ref            # 引用号
        self.digest = sha(content)
        self.issued_at = now()

    def __repr__(self):
        return f"Evidence({self.kind}/{self.ref}/{self.digest})"


class Gate:
    """门禁：状态转换前置条件。条件不满足 ⇒ 转换无效（DENIED 回执）"""

    REQUIRED_EVIDENCE = {
        "REGISTER":  [],  # 注册只需身份齐备
        "ACTIVATE":  ["bench_test", "clinical_review"],
        "REVERIFY":  ["bench_test"],
        "RESUME":    ["bench_test", "release_note"],
        "MODEL_CHANGE": ["version_manifest", "bench_test", "clinical_review"],
    }

    @staticmethod
    def check(transition: str, evidence: list) -> tuple:
        need = Gate.REQUIRED_EVIDENCE.get(transition, [])
        have = {e.kind for e in evidence}
        missing = [k for k in need if k not in have]
        ok = not missing
        return ok, missing


class Registry:
    """有籍：Agent / 模型 / 工具 / 数据集都有身份、版本、权限"""

    def __init__(self):
        self.entries = {}

    def register(self, eid: str, etype: str, version: str, perms: list) -> str:
        rec = {"type": etype, "version": version, "perms": perms,
               "registered_at": now(), "status": "REGISTERED"}
        self.entries[eid] = rec
        return f"REG-{sha(eid + version)}"

    def get(self, eid):
        return self.entries.get(eid)


class MedAIAgent:
    """
    虚构医疗器械 AI Agent：影像分诊 Agent（演示用，非真实产品）
    状态机：REGISTERED → GATE_PASSED → ACTIVE → PAUSED → ROLLBACK
            → REVERIFY → RESUMED （或任意环节 → DENIED / RETIRED）
    """
    STATES = ["REGISTERED", "GATE_PASSED", "ACTIVE", "ANOMALY", "PAUSED",
              "ROLLBACK", "REVERIFY", "RESUMED", "DENIED", "RETIRED"]

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = "REGISTERED"
        self.evidence: list = []
        self.model_version = "v1.0"
        self.log: list = []

    # ---------- 生命周期 ----------
    def submit_evidence(self, ev: Evidence):
        self.evidence.append(ev)
        self._log("EVIDENCE_SUBMIT", f"{ev}")

    def activate(self) -> bool:
        ok, missing = Gate.check("ACTIVATE", self.evidence)
        if ok:
            self.state = "GATE_PASSED"
            self._log("GATE", "ACTIVATE 证据齐备 → GATE_PASSED")
            self.state = "ACTIVE"
            self._log("EXECUTE", "Agent 进入 ACTIVE，开始执行（虚构分诊任务）")
        else:
            self.state = "DENIED"
            self._log("GATE", f"ACTIVATE 证据缺失 {missing} → DENIED（转换无效）")
        return ok

    def monitor(self, metrics: dict, rules: list):
        """持续监测：准确率没降 ≠ 没问题——静默失败规则在这里接住"""
        self._log("MONITOR", f"指标 {metrics}")
        fired = []
        for rule in rules:
            if rule["signal"] in metrics and rule["condition"](metrics):
                fired.append(rule)
                self._log("ANOMALY", f"静默失败命中 {rule['id']}: {rule['name']}")
        if fired:
            self.state = "ANOMALY"
            self.pause(fired)
        else:
            self._log("MONITOR", "无异常，继续 ACTIVE")

    def pause(self, fired_rules):
        self.state = "PAUSED"
        for r in fired_rules:
            self._log("PAUSE", f"{r['id']} → Gate 动作: {r['gate_action']}")

    def rollback(self, to_version: str):
        self.state = "ROLLBACK"
        self._log("ROLLBACK", f"模型回退 {self.model_version} → {to_version}")
        self.model_version = to_version

    def reverify(self) -> bool:
        self.state = "REVERIFY"
        ok, missing = Gate.check("REVERIFY", self.evidence)
        self._log("REVERIFY", "重验证据齐备 → 通过" if ok else f"缺 {missing} → 不通过")
        return ok

    def resume(self) -> bool:
        ok, missing = Gate.check("RESUME", self.evidence)
        if ok:
            self.state = "RESUMED"
            self._log("RESUME", "🟢 RESUMED —— 资格非单调重估通过，Agent 恢复运行")
        else:
            self.state = "PAUSED"
            self._log("RESUME", f"恢复证据缺失 {missing} → 维持 PAUSED")
        return ok

    # ---------- Change-Gate 子链 ----------
    def request_model_change(self, new_version: str, new_evidence: list):
        """变更重估只看【本次变更提交的新证据】，不吃历史累积证据"""
        self._log("CHANGE_DETECT", f"检测到模型变更请求 {self.model_version} → {new_version}")
        self.evidence.extend(new_evidence)
        ok, missing = Gate.check("MODEL_CHANGE", new_evidence)
        if ok:
            self._log("RISK_REASSESS", "变更风险重估：通过（虚构基准对比）")
            self._log("CHANGE_GATE", f"模型变更 {new_version} → 发布（APPROVED）")
            self.model_version = new_version
            return True
        self._log("CHANGE_GATE", f"模型变更 → 拒绝/回滚（缺失 {missing}）")
        return False

    # ---------- 输出 ----------
    def _log(self, action: str, detail: str):
        self.log.append({"t": now(), "state": self.state, "action": action, "detail": detail})
        print(f"  [{action:>13}] {detail}")

    def receipt(self) -> dict:
        """审计回执：有籍·有证·有门禁的留痕"""
        return {
            "agent_id": self.agent_id,
            "final_state": self.state,
            "model_version": self.model_version,
            "evidence_count": len(self.evidence),
            "chain_digest": sha(json.dumps([e.digest for e in self.evidence])),
            "log_entries": len(self.log),
        }


def load_rules() -> list:
    with open(RULES_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    # 条件以受限表达式求值（演示内嵌，不 eval 任意代码）
    conds = {
        "drift": lambda m: m.get("drift", 0) > 0.25,
        "path":  lambda m: m.get("path_deviation", False) is True,
        "stale": lambda m: m.get("data_age_days", 0) > 30,
    }
    rules = []
    for r in raw["rules"]:
        rules.append({**r, "condition": conds[r["cond_key"]]})
    return rules


def main():
    print("=" * 68)
    print("LGD-MedAI Demo v0.1（虚构场景 · 零真实患者数据 · 内部演示）")
    print("=" * 68)

    registry = Registry()
    rules = load_rules()

    # ── 有籍：四类实体全部入册 ──────────────────────────────
    print("\n■ 第一幕：注册（有籍 Registry）")
    registry.register("agent-triage-01", "AGENT", "v1.0", ["classify", "retrieve"])
    registry.register("model-img-cls",   "MODEL", "v1.0", ["inference"])
    registry.register("tool-imaging-db", "TOOL",  "v2026.09", ["read"])
    registry.register("data-cohort-sim", "DATASET", "sim-2026Q3", ["train", "validate"])
    for eid, rec in registry.entries.items():
        print(f"  ✔ {eid:<18} {rec['type']:<8} {rec['version']:<10} perms={rec['perms']}")

    # ── 有证 + 门禁：证据不足被拒 → 补齐 → 放行 ────────────
    print("\n■ 第二幕：门禁（有证 Evidence · 有门禁 Gate）——先拒后放")
    agent = MedAIAgent("agent-triage-01")
    agent.submit_evidence(Evidence("bench_test", "BENCH-001", "虚构基准：敏感性/特异性达标"))
    agent.activate()                       # 缺 clinical_review → DENIED
    agent.state = "REGISTERED"             # 重新排队（补证据）
    agent.submit_evidence(Evidence("clinical_review", "CLIN-001", "虚构临床复核记录"))
    agent.activate()                       # 齐 → ACTIVE

    # ── Change-Gate 子链（先演示拒绝，再放行） ─────────────
    print("\n■ 第三幕前置：Change-Gate 模型 v1.0 → v1.1（先拒后放）")
    agent.request_model_change("v1.1", [
        Evidence("version_manifest", "VM-1.1", "变更清单：阈值调优"),
        Evidence("bench_test", "BENCH-003", "v1.1 基准"),
    ])                                       # 缺本变更的 clinical_review → 拒绝
    # 补齐 manifest + bench + clin → APPROVED
    agent.request_model_change("v1.1", [
        Evidence("version_manifest", "VM-1.1b", "变更清单：阈值调优"),
        Evidence("bench_test", "BENCH-003b", "v1.1 基准"),
        Evidence("clinical_review", "CLIN-002", "v1.1 临床复核"),
    ])

    # ── 监测 + 静默失败 + 暂停/回退/重验/恢复 ──────────────
    print("\n■ 第四幕：监测 → 静默失败 → 暂停 → 回退 → 重验 → 恢复")
    agent.monitor({"accuracy": 0.91, "drift": 0.05}, rules)          # 正常
    agent.monitor({"accuracy": 0.91, "drift": 0.41}, rules)          # 人群漂移（准确率没降！）
    agent.submit_evidence(Evidence("bench_test", "BENCH-002", "回退后重验基准"))
    agent.rollback("v1.0")                  # v1.1 → v1.0
    agent.reverify()
    agent.submit_evidence(Evidence("release_note", "RN-002", "恢复说明与监测计划"))
    agent.resume()                          # 🟢 RESUMED

    # ── 审计回执 ──────────────────────────────────────────
    print("\n■ 审计回执（有籍·有证·有门禁 留痕）")
    print(json.dumps(agent.receipt(), ensure_ascii=False, indent=2))

    expected = "RESUMED"
    print("\n验收：final_state = %s → %s" % (
        agent.state, "✅ PASS" if agent.state == expected else "❌ FAIL"))
    return 0 if agent.state == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
