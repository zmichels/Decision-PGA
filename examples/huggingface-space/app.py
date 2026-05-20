from __future__ import annotations

import json

import gradio as gr

from decision_pga.cli import diagnose_payload


EXAMPLES = {
    "Tool/action ambiguity": {
        "source": "probability_cloud",
        "label": "agent tool-action ambiguity",
        "labels": ["search_docs", "query_database", "ask_clarifying_question", "draft_answer"],
        "probabilities": [
            [0.46, 0.42, 0.08, 0.04],
            [0.43, 0.45, 0.08, 0.04],
            [0.47, 0.40, 0.09, 0.04],
            [0.41, 0.47, 0.08, 0.04],
            [0.45, 0.43, 0.08, 0.04],
            [0.42, 0.46, 0.08, 0.04],
        ],
    },
    "RAG evidence conflict": {
        "source": "probability_cloud",
        "label": "RAG evidence conflict",
        "labels": ["answer_with_retrieval_a", "answer_with_retrieval_b", "retrieve_more_context", "abstain"],
        "probabilities": [
            [0.49, 0.38, 0.09, 0.04],
            [0.43, 0.44, 0.09, 0.04],
            [0.51, 0.36, 0.09, 0.04],
            [0.38, 0.49, 0.09, 0.04],
            [0.45, 0.43, 0.08, 0.04],
            [0.41, 0.47, 0.08, 0.04],
        ],
    },
    "Document extraction routing": {
        "source": "probability_cloud",
        "label": "document extraction routing with missing context",
        "labels": ["accept_extraction", "ask_for_clarification", "retrieve_more_context", "flag_for_review", "defer"],
        "probabilities": [
            [0.18, 0.20, 0.30, 0.18, 0.14],
            [0.22, 0.17, 0.27, 0.19, 0.15],
            [0.16, 0.22, 0.29, 0.17, 0.16],
            [0.20, 0.18, 0.24, 0.22, 0.16],
            [0.19, 0.21, 0.25, 0.18, 0.17],
            [0.17, 0.20, 0.28, 0.20, 0.15],
        ],
    },
    "Multi-step agent drift": {
        "source": "trajectory_steps",
        "label": "multi-step agent drift",
        "labels": ["retrieve_evidence", "draft_answer", "ask_user", "abstain"],
        "steps": ["retrieve_evidence"] * 6 + ["draft_answer"] * 6,
        "window_size": 3,
        "step": 3,
    },
    "Stable abstain decision": {
        "source": "probability_cloud",
        "label": "stable abstain decision",
        "labels": ["answer_now", "retrieve_more_context", "route_to_reviewer", "abstain"],
        "probabilities": [
            [0.05, 0.08, 0.10, 0.77],
            [0.04, 0.09, 0.11, 0.76],
            [0.06, 0.07, 0.10, 0.77],
            [0.05, 0.08, 0.09, 0.78],
            [0.04, 0.10, 0.10, 0.76],
            [0.05, 0.08, 0.11, 0.76],
        ],
    },
}


def load_example(name: str) -> str:
    return json.dumps(EXAMPLES[name], indent=2)


def run_diagnostic(payload_text: str) -> str:
    payload = json.loads(payload_text)
    result = diagnose_payload(payload)
    return json.dumps(result, indent=2)


with gr.Blocks(title="Decision-PGA Agent Diagnostic Demo") as demo:
    gr.Markdown(
        """
        # Decision-PGA Agent Diagnostic Demo

        Pick a synthetic agent decision scenario and run the local diagnostic.
        The examples are synthetic and model-neutral; no model APIs are called.
        """
    )
    scenario = gr.Dropdown(
        choices=list(EXAMPLES),
        value="Tool/action ambiguity",
        label="Scenario",
    )
    payload = gr.Code(
        value=load_example("Tool/action ambiguity"),
        language="json",
        label="Diagnostic payload",
    )
    output = gr.Code(language="json", label="Diagnostic output")
    scenario.change(load_example, inputs=scenario, outputs=payload)
    gr.Button("Run diagnostic").click(run_diagnostic, inputs=payload, outputs=output)
    gr.Markdown(
        """
        Canonical article: https://zmichels.github.io/decision-pga-pages/article/

        Public code: https://github.com/zmichels/Decision-PGA
        """
    )


if __name__ == "__main__":
    demo.launch()
