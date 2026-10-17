# Shared design contract

Before UI implementation, follow [upstream expert review](WORKFLOW.md). Wait for
material user decisions, clarify consequential ambiguity and record authorization.
Exact specified/delegated corrections need no repeated approval.

Use one vocabulary, component system and authoritative state across relevant
surfaces. Configure actual tokens/type/spacing/contrast in your project's owning
UI library before implementing product screens; no Android-specific palette or
orientation is imposed by this template. Prefer minimal, discoverable actions,
visible current values, loading feedback, accessible names and useful recovery.
Fewer taps do not justify sacrificing working space or hiding essential actions.

Specify Up/Back/Close/outside dismissal, keyboard/focus, selected/disabled/loading/
error/cancel behavior and compact/expanded layouts. If placement/grouping/action
access remains unclear, ask the user after expert review rather than inventing it.

Acceptance inspects real representative rendered surfaces and interactions under
declared bounds/input/lifecycle states. Do not silently approve goldens. Visual,
functional and performance conclusions are separately scoped; measurements need
sample counts, timing boundaries and p50/p95 where applicable.
