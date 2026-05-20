# Community Engagement Setup

The first public awareness push should help the right people do one useful
thing: bring a real workflow-shaped question to the project. The repo should
make that easy without asking for private data or overclaiming what the
prototype can do.

## GitHub Discussions

Enable GitHub Discussions in repository settings and create these categories:

- `use cases`
- `agent integration`
- `uncertainty/metrics`
- `document extraction workflows`

The templates in `.github/DISCUSSION_TEMPLATE/` give each category a lightweight
starter form. GitHub category creation is a repository setting, so the files
prepare the discussion surface but do not enable Discussions by themselves.

## Issue Flow

Use issue templates for:

- adapter requests;
- diagnostic scenarios;
- MCP integration issues;
- example contributions.

Ask contributors to keep payloads synthetic, public, or anonymized. Do not ask
for private documents, credentials, patient data, or provider responses that
contain sensitive content.

## Launch Rhythm

Start with a small, high-signal circle:

1. Share the article/demo with collaborators already interested in agent
   workflow diagnostics.
2. Point developers to `docs/agent-toolkit.md` and the `examples/agent/`
   payloads.
3. Ask for one concrete scenario per person: what decision cloud would they want
   an agent to diagnose?
4. Convert recurring requests into examples, adapter issues, benchmark fixtures,
   or short docs.

The goal is not mass attention first. The goal is useful contact with people
who can say whether the diagnostic contract helps real agent workflows.

## Good first asks

When sharing the project, ask for concrete examples rather than general
approval:

- "Where does your agent currently choose between proceed, clarify, retrieve,
  review, abstain, or replan?"
- "Where do confidence or entropy feel too blunt?"
- "Can you describe a synthetic version of that decision state?"
- "What would make this easy to call from your agent framework?"

These questions give the project useful material even when the answer is "this
is redundant with our current telemetry."
