🟢 **High confidence**

# Phase 4F review panel prototype

The local panel wraps the existing live `apose_ue_review.rigreview`. The backend, correction model and anatomy criteria are unchanged. John/Jane are the primary subjects. The guided sequence supports the intended beginner wizard direction; explicit body/finger controls remain available.

## Launch

Current editor: the bridge is attached and John is ready at the neck step. Open [the panel](http://127.0.0.1:8746/).

To reopen/start the local host:

    & 'E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase4F\ReviewPanel\Launch.ps1'

For the already loaded/open review after a new editor attachment, use its Python console once:

    from ReviewPanel import bridge; bridge.attach()

Fresh-editor setup and the planner's complete review procedure are in [ChatGPTPlannerReviewManual.md](../ChatGPTPlannerReviewManual.md). That is the standalone manual to upload to the ChatGPT project's source files.

## Implementation

| New source | Responsibility |
| --- | --- |
| `Working/Phase4F/ReviewPanel/bridge.py` | UE main-thread callback; reads live state and dispatches existing backend methods; guided step metadata |
| `Working/Phase4F/ReviewPanel/server.py` | Python standard-library loopback host; same-origin/token protected command submission |
| `Working/Phase4F/ReviewPanel/panel.html` | Guided Accept/Adjust/Unsure steps, explicit controls, progress, canonical Light/Dark tokens |
| `Working/Phase4F/ReviewPanel/Launch.ps1` | Starts the host hidden and opens its loopback browser address |
| `Working/Phase4F/ReviewPanel/check_panel.py` | Eight isolated wrapper checks; never exports a real session |
| `Working/Phase4F/ReviewPanel/check_ui.cjs` | Isolated fake-DOM/transport checks including acceptance advance and explicit digit identity |
| `Working/Phase4F/ReviewPanel/validate_navigation.py` | Navigation-only live check; cannot submit human review/placement/identity/start/finish |

Transport state is confined to `Working/Phase4F/ReviewPanel/runtime`. Commands bind to attachment, character, session and revision, expire, and are claimed before execution without automatic replay. It is IPC state, not a human review ledger. Attachment and progress polling never call core export or add events. User actions call the same backend methods as the console workflow.

The agent navigation route temporarily suppresses only the backend's navigation event hook in a `try/finally`, restoring it immediately. Its allowed actions exclude all anatomical evidence-writing commands. Validation never claims an agent action as human review.

## Verified results

- Attached to the existing editor object, with John's trial already in progress and pelvis already accepted without movement.
- Opened Jane and John through the actual panel. Jane remains unstarted. Progress changed appropriately for each subject.
- Jane's unresolved Head pivot selection and camera transition, Front view, and left track-2 highlight completed through panel buttons without a started trial or any new event.
- John's unresolved `neck_01` selection and side camera completed through the navigation-only route. The published UE selected-controls list confirmed `neck_01`; no movement is pending.
- John retains exactly seven genuine events, one review, one accepted pelvis, zero placements, zero identifications, zero moved landmarks, and the original session ID. Jane retains zero events.
- All 91 baseline files across both subjects' Working/Documentation folders are byte-for-byte unchanged, including sessions, immutable events and approval artefacts. [Preservation baseline](preservation_before.json); [final validation](validation.json).
- Python syntax, eight isolated wrapper tests and the isolated UI behaviour suite pass. Accept/advance, count refresh, summary stability, explicit identity, disconnect guards, stale/expired requests and pending-position protection are covered without real anatomical actions.
- Actual browser checks cover first-use Light, persisted Dark after reload, restoration to Light, 3px keyboard focus, desktop layout and 420px layout without horizontal overflow. No animation is used; reduced-motion CSS is present.
- Canonical contrast minima: Light normal text 4.93:1 / functional borders 3.63:1 / status marks 3.44:1; Dark 5.43:1 / 3.13:1 / 4.87:1. Muted text also meets 4.5:1 on its permitted surfaces. [Theme checks](theme_checks.json); [panel screenshot](panel_john.png).

Reproduce the isolated checks from the project root:

    python -B Working\Phase4F\ReviewPanel\check_panel.py
    node Working\Phase4F\ReviewPanel\check_ui.cjs

Python is required for the host; Node is only needed for the development UI check. Tests use captured delivery snapshots, not the evolving real trial. `john_state_at_attachment.json` and `panel_status_at_attachment.json` are static audit/test fixtures and must never be restored into a live session.

## Limits and self-review

This remains a prototype local browser panel, with one-time UE Python attachment after restart and UE gizmo placement. Cameras are existing backend presets. The review summary and Anatomy validation stages are informational; the panel does not rerun gates or generate downstream assets. Real acceptance/identity/placement paths were verified by isolated delegation/behaviour checks, not by fabricating user actions in either real trial.

The backend records selected pending controls then redraws, so record deliberate gizmo changes promptly and avoid unrelated unrecorded drags. Save/Finish can have partial success if a later export/level save fails; refresh and inspect the backend state before retrying. An unacknowledged claimed command is never replayed automatically.

Level 1 single-agent self-review checked live object reuse, all backend method mappings, provenance, explicit identity, stale-session safety, no automatic start/approval, pending-change protection, error handling, UI continuity, accessibility, and preservation. The final visual critique removed the empty stretched progress column and translated finger keys into Left/Right digit names. No prior-phase source/evidence or gate logic was edited. The workspace has no `.git` directory; no Git operation, commit or push was performed.

The earlier 66/106 and 65/106 gate snapshots remain historical until the existing validators run against genuine completed review evidence. No anatomy gate has been declared passed and no downstream work is authorised by this prototype.
