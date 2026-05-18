"""Application-gap evaluation layer for Decision-PGA.

This module is intentionally model-free. It turns the current Decision-PGA
surface area into a deterministic review matrix that can guide the next
hands-on evaluation work without implying production validation.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Literal


FitLabel = Literal["promising", "redundant", "needs_adapter", "inconclusive"]

APPLICATION_GAP_FAMILIES = (
    "tool_action_ambiguity",
    "clarification_abstention",
    "rag_evidence_conflict",
    "hallucination_uncertainty",
    "instruction_following_risk",
    "multi_step_agent_drift",
    "decision_monitoring",
)

GAP_MATRIX_FIELDS = (
    "gap_family",
    "use_case",
    "current_failure_mode",
    "decision_pga_contribution",
    "baseline_comparison",
    "implementation_difficulty",
    "fit_label",
    "recommended_next_step",
)


@dataclass(frozen=True)
class ApplicationScenario:
    """One candidate application gap and its conservative Decision-PGA fit."""

    gap_family: str
    use_case: str
    touchstone: str
    expected_reading: str
    current_failure_mode: str
    decision_pga_contribution: str
    baseline_comparison: str
    baseline_reading: str
    pga_reading: str
    incremental_value: str
    implementation_difficulty: str
    fit_label: FitLabel
    recommended_next_step: str
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible scenario payload."""

        return {
            "gap_family": self.gap_family,
            "use_case": self.use_case,
            "touchstone": self.touchstone,
            "expected_reading": self.expected_reading,
            "current_failure_mode": self.current_failure_mode,
            "decision_pga_contribution": self.decision_pga_contribution,
            "baseline_comparison": self.baseline_comparison,
            "baseline_reading": self.baseline_reading,
            "pga_reading": self.pga_reading,
            "incremental_value": self.incremental_value,
            "implementation_difficulty": self.implementation_difficulty,
            "fit_label": self.fit_label,
            "recommended_next_step": self.recommended_next_step,
            "evidence": list(self.evidence),
        }

    def gap_matrix_row(self) -> dict[str, str]:
        """Return the compact matrix row used in reports and CSV exports."""

        payload = self.to_dict()
        return {
            field: str(payload[field])
            for field in GAP_MATRIX_FIELDS
        }


@dataclass(frozen=True)
class ApplicationEvaluationReport:
    """A deterministic application-gap review for Decision-PGA."""

    scenarios: tuple[ApplicationScenario, ...]
    summary: dict[str, object]

    def scenario_by_gap(self, gap_family: str) -> ApplicationScenario:
        """Return the scenario for a gap family, or raise a clear error."""

        for scenario in self.scenarios:
            if scenario.gap_family == gap_family:
                return scenario
        raise ValueError(f"unknown application gap family: {gap_family}")

    def gap_matrix_rows(self) -> list[dict[str, str]]:
        """Return compact gap matrix rows with stable column names."""

        return [scenario.gap_matrix_row() for scenario in self.scenarios]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible report payload."""

        return {
            "source": "application_evaluation",
            "summary": self.summary,
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
            "gap_matrix": self.gap_matrix_rows(),
        }


def run_application_evaluation_suite() -> ApplicationEvaluationReport:
    """Return the deterministic Decision-PGA application-gap review suite."""

    scenarios = _application_scenarios()
    if tuple(scenario.gap_family for scenario in scenarios) != APPLICATION_GAP_FAMILIES:
        raise ValueError("application scenarios must match APPLICATION_GAP_FAMILIES order.")

    fit_counts = Counter(scenario.fit_label for scenario in scenarios)
    promising = [
        scenario.gap_family
        for scenario in scenarios
        if scenario.fit_label == "promising"
    ]
    adapter_needed = [
        scenario.gap_family
        for scenario in scenarios
        if scenario.fit_label == "needs_adapter"
    ]
    summary: dict[str, object] = {
        "scenario_count": len(scenarios),
        "gap_families": list(APPLICATION_GAP_FAMILIES),
        "fit_counts": dict(sorted(fit_counts.items())),
        "recommended_deep_dives": [
            {
                "direction": "agent tool/action selection",
                "gap_family": "tool_action_ambiguity",
                "why": "The current model-output and provider-score adapters already map naturally to action candidates.",
            },
            {
                "direction": "RAG/evidence conflict",
                "gap_family": "rag_evidence_conflict",
                "why": "It is likely important, but needs a claim/evidence adapter before PGA can be evaluated fairly.",
            },
        ],
        "promising_gaps": promising,
        "adapter_needed_gaps": adapter_needed,
        "claim": (
            "Decision-PGA is most credible today as a local diagnostic scaffold for "
            "action-choice ambiguity, trajectory drift, and monitoring. Evidence-conflict "
            "and hallucination use cases are important but need adapters before claims "
            "can be tested."
        ),
    }
    return ApplicationEvaluationReport(scenarios=scenarios, summary=summary)


def _application_scenarios() -> tuple[ApplicationScenario, ...]:
    return (
        ApplicationScenario(
            gap_family="tool_action_ambiguity",
            use_case="agent tool/action selection",
            touchstone="Do probability-cloud metrics reveal whether an agent should call, clarify, abstain, or replan?",
            expected_reading="Structured binary or diffuse action uncertainty should trigger safer control decisions before side effects occur.",
            current_failure_mode="Agents can choose among tools from fragile descriptions or shallow score differences, then execute irreversible calls.",
            decision_pga_contribution="Measures whether candidate-action scores form a tight decision, a two-action ambiguity, broad uncertainty, or a regime shift.",
            baseline_comparison="Compare against entropy, top-1 margin, and top-label switch rate on the same action-candidate fixtures.",
            baseline_reading="Entropy and margin can flag low confidence but often miss whether uncertainty is concentrated between two actions or scattered.",
            pga_reading="PC1 fraction, anisotropy, and geodesic drift can separate binary tool ambiguity from diffuse action uncertainty.",
            incremental_value="Potentially adds an interpretable action-state contract for proceed, clarify, gather evidence, or replan.",
            implementation_difficulty="medium",
            fit_label="promising",
            recommended_next_step="Deep-dive candidate: build a tool/action selection fixture set and compare PGA against entropy, margin, and switch-rate baselines.",
            evidence=(
                "Existing Decision-PGA provider-score adapters already accept candidate-action score maps.",
                "Function-calling UQ work identifies tool execution confidence as a distinct need.",
                "Tool-preference reliability work suggests selection can be fragile under competing descriptions.",
            ),
        ),
        ApplicationScenario(
            gap_family="clarification_abstention",
            use_case="structured clarification and abstention gating",
            touchstone="Can a diagnostic choose between proceed, ask a targeted question, gather evidence, or abstain?",
            expected_reading="Low-margin structured ambiguity should point to clarification; diffuse uncertainty should point to evidence gathering.",
            current_failure_mode="Agents often ask too many questions, ask the wrong question, or proceed when the task is under-specified.",
            decision_pga_contribution="Turns score clouds over next actions into a compact state/action recommendation that can sit beside EVPI-style policies.",
            baseline_comparison="Compare PGA action recommendations against entropy-only, margin-only, and fixed-threshold abstention.",
            baseline_reading="A scalar uncertainty threshold can decide to stop, but rarely explains which uncertainty shape caused the stop.",
            pga_reading="Binary ambiguity and diffuse uncertainty map to different next actions in the current diagnostic contract.",
            incremental_value="Useful as a lightweight pre-policy gate, especially when paired with a separate question-value model.",
            implementation_difficulty="medium",
            fit_label="promising",
            recommended_next_step="Add clarification fixtures where labels are next actions, then measure whether PGA routes binary ambiguity to targeted questions more reliably than entropy.",
            evidence=(
                "The current diagnostic already emits clarify_between_top_labels and gather_more_evidence.",
                "Structured clarification research shows the need to separate specification uncertainty from model uncertainty.",
            ),
        ),
        ApplicationScenario(
            gap_family="rag_evidence_conflict",
            use_case="RAG/evidence conflict diagnostics",
            touchstone="Can a report distinguish one weak evidence set from competing evidence clusters?",
            expected_reading="Conflicting evidence should look like structured ambiguity over claims, sources, or answer paths rather than generic high entropy.",
            current_failure_mode="RAG systems can retrieve mixed, stale, adversarial, or mutually inconsistent evidence while still producing fluent answers.",
            decision_pga_contribution="Could analyze probability clouds over claim clusters, source groups, or answer paths once a stable adapter exists.",
            baseline_comparison="Compare against answer entropy, retrieval overlap, source count, and evidence-score variance.",
            baseline_reading="Retrieval metrics expose recall or ranking, but do not directly describe the geometry of competing answer decisions.",
            pga_reading="A claim/evidence adapter could reveal whether uncertainty is one dominant conflict axis or a broad evidence failure.",
            incremental_value="Promising but not testable honestly until claim clustering and evidence-to-label adapters are defined.",
            implementation_difficulty="high",
            fit_label="needs_adapter",
            recommended_next_step="Deep-dive candidate: build a RAG/evidence conflict adapter that maps retrieved support into claim-cluster probability clouds.",
            evidence=(
                "RAG review literature emphasizes uncertainty-aware control, provenance, safety, and holistic benchmarks.",
                "Semantic-entropy work shows semantic clustering can matter more than token-level uncertainty for free-form answers.",
            ),
        ),
        ApplicationScenario(
            gap_family="hallucination_uncertainty",
            use_case="hallucination and confabulation triage",
            touchstone="Can resampled answers be converted into decision clouds that distinguish stable meaning from unstable claims?",
            expected_reading="Confabulation risk should appear as dispersion over incompatible semantic claims, not mere wording variation.",
            current_failure_mode="Token entropy and lexical diversity can overcount harmless phrasing variation or miss consistently wrong claims.",
            decision_pga_contribution="Could operate downstream of semantic clustering by measuring the geometry of claim-cluster probability clouds.",
            baseline_comparison="Compare against semantic entropy, self-checking, token entropy, and answer-consistency baselines.",
            baseline_reading="Semantic entropy is already strong for this gap; Decision-PGA may be redundant unless it improves action routing or shape interpretation.",
            pga_reading="PGA could add binary-vs-diffuse claim-state interpretation after semantic labels are available.",
            incremental_value="Likely complementary rather than replacement; needs semantic claim adapters and direct benchmark comparison.",
            implementation_difficulty="high",
            fit_label="needs_adapter",
            recommended_next_step="Prototype a semantic-cluster adapter before claiming any hallucination-detection advantage.",
            evidence=(
                "Semantic entropy directly targets confabulation by clustering meaning-equivalent generations.",
                "Decision-PGA currently avoids semantic parsing and therefore cannot detect factuality by itself.",
            ),
        ),
        ApplicationScenario(
            gap_family="instruction_following_risk",
            use_case="instruction-following uncertainty",
            touchstone="Can the method detect subtle compliance risk before an agent acts?",
            expected_reading="Constraint-sensitive tasks need uncertainty over instruction satisfaction, not only answer or action confidence.",
            current_failure_mode="Models can be confident while subtly violating formatting, scope, safety, or multi-constraint instructions.",
            decision_pga_contribution="Could summarize probability clouds over compliance labels if a verifier or rubric supplies candidate scores.",
            baseline_comparison="Compare against verifier confidence, self-rated confidence, entropy, and rule-specific failure rates.",
            baseline_reading="Existing uncertainty methods can struggle on subtle instruction-following errors, especially when confidence remains high.",
            pga_reading="PGA may help only after a verifier creates a meaningful compliance-label cloud.",
            incremental_value="Currently uncertain; the bottleneck is a trustworthy adapter/verifier, not the geometry kernel.",
            implementation_difficulty="high",
            fit_label="inconclusive",
            recommended_next_step="Keep as a research candidate after tool/action and RAG adapters are evaluated.",
            evidence=(
                "Instruction-following UQ studies report difficulty isolating subtle compliance uncertainty.",
                "Decision-PGA is model-neutral and will inherit weaknesses from any compliance-score adapter.",
            ),
        ),
        ApplicationScenario(
            gap_family="multi_step_agent_drift",
            use_case="multi-step agent drift and replanning",
            touchstone="Can series-style diagnostics reveal when an agent trajectory changes decision regime?",
            expected_reading="A stable local step can still contribute to cumulative drift across a plan or tool chain.",
            current_failure_mode="Final-answer uncertainty misses uncertainty that accumulates across intermediate decisions and environment interactions.",
            decision_pga_contribution="Existing trajectory adapters can turn step sequences into sliding-window probability clouds for drift/state reports.",
            baseline_comparison="Compare against final-step entropy, step-count heuristics, and raw action-switch rates.",
            baseline_reading="Switch rates see churn but not whether changes are coherent regime shifts or diffuse uncertainty.",
            pga_reading="Half-window geodesic distance and state transitions can flag segment-or-replan conditions.",
            incremental_value="Good bridge from the current API into agent runtime monitoring.",
            implementation_difficulty="medium",
            fit_label="promising",
            recommended_next_step="Add trajectory fixture reports modeled on the SO3-PGA series workflow, with static plots in a later slice.",
            evidence=(
                "The current source adapters already diagnose trajectory_steps locally.",
                "Agent uncertainty-propagation work highlights limitations of final-output-only uncertainty.",
            ),
        ),
        ApplicationScenario(
            gap_family="decision_monitoring",
            use_case="runtime decision monitoring and regression checks",
            touchstone="Can a local tool detect state regressions as prompts, tools, retrieval stores, or models change?",
            expected_reading="Stable benchmarks should stay stable; emerging ambiguity, diffusion, or drift should produce explicit state changes.",
            current_failure_mode="Teams monitor accuracy, latency, and cost, but may miss shape changes in decision distributions before failures surface.",
            decision_pga_contribution="Provides deterministic JSON/CSV reports that can be run in CI, eval harnesses, or MCP clients.",
            baseline_comparison="Compare against aggregate accuracy, mean entropy, mean margin, and alert thresholds.",
            baseline_reading="Aggregate metrics can hide that the same error rate now comes from a different and riskier decision-state shape.",
            pga_reading="PGA state and dispersion metrics can flag distribution-shape changes as testable regression artifacts.",
            incremental_value="Useful for local monitoring if paired with representative fixtures and acceptance thresholds.",
            implementation_difficulty="low",
            fit_label="promising",
            recommended_next_step="Add a fixture-regression command that compares current diagnostics with checked-in expected states.",
            evidence=(
                "The evaluation CLI already emits machine-readable benchmark and report artifacts.",
                "Decision-PGA tools are deterministic and local, making them easy to run in CI.",
            ),
        ),
    )
