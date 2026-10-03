# Run → Jump → Land skid correction

🟢 **High confidence** — native technical verification passed on Female and Aegis. Final hands-on acceptance remains pending.

## Symptom and measurements

The unchanged accepted reviews reproduced the reported skid using native PlayerController input: Shift + W, Space, then continued forward input.

| Subject | Touchdown velocity | Landing-to-run selection delay | Distance during landing hold | Corrected moving-landing hold |
| --- | --- | --- | --- | --- |
| Female | 600 cm/s | 0.867644 s | 520.587 cm | 0 s / 0 cm at observed touchdown sample |
| Aegis | 600 cm/s | 0.869603 s | 521.762 cm | 0 s / 0 cm at observed touchdown sample |

Horizontal velocity remained 600 cm/s before jump, in flight, at touchdown and throughout the old landing hold. MovementMode returned to Walking at touchdown. Input remained active; no Landed callback or velocity override exists in the Character graph. Mesh translation follows capsule translation with the retained capsule-height offset. Root translation relative to the mesh was constant throughout the landing hold: 0 cm excursion.

The corrected zero values describe **branch selection**, not zero pose-blend duration. The existing 0.1 s air-to-ground blend remains. Native player blend weights were unavailable; no independently measured blend-completion claim is made. Native sequence time and bone-position samples confirm that run/walk actually advance after touchdown.

## Landing clip and root-motion inspection

Source, unchanged:

`/Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/Sources/InstalledMannequins/Anims/Unarmed/Jump/MM_Land.MM_Land`

Destinations, unchanged:

- `/Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/Animations/LibraryV1/Jump/MM_Land.MM_Land`
- `/Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/Animations/LibraryV1/Jump/MM_Land.MM_Land`

All three: 0.866667 s, 30 fps, 26 frames / 27 keys; EnableRootMotion=false, ForceRootLock=true, ReferencePose lock, normalised root-motion scale=true. Raw source and destination root trajectories have **zero excursion**. Pelvis excursions are 22.461 cm source, 12.220 cm Female and 23.006 cm Aegis. The stationary-root landing/recovery pose was being carried forward by the capsule, rather than performing a running stride. This is a planted landing selection mismatch; there is no authored forward root motion to strip.

Runtime root mode is RootMotionFromMontagesOnly; these SequencePlayers do not apply root motion to actor movement. No bake defect or double translation was found.

## Confirmed cause and smallest correction

Classes: `LANDING_STATE_HELD_TOO_LONG` and `ANIMATION_VISUAL_PLANT_VS_CONTINUED_WORLD_MOVEMENT`.

Original flow:

- Ground → air: IsFalling.
- Jump → fall: no longer rising, or AirTime reaches jump duration.
- Touchdown: WasAirborne && !Airborne starts the full 0.866667 s LandTime.
- Land selected whenever LandTime>0 && !Airborne, regardless of horizontal speed.
- Ground selection resumes only when that timer expires.

The isolated correction adds **Speed<=5** to the original Landing predicate. This reuses the exact existing idle/walk boundary. Stationary touchdown retains the full land clip; moving touchdown blends directly to existing grounded walk/run. Starting movement during stationary recovery also releases the planted pose. No new landing-duration tuning is introduced.

Only three EventGraph nodes were added per copied AnimBP. The original nodes differ only in the two connections required to insert this guard. AnimGraph, 0.1 s air/landing blends, 0.15 s ground blends, Character input graph and CharacterMovement settings remain structurally unchanged.

Movement settings remain: walk 300 / Shift run 600 cm/s, walking braking 1500 cm/s², ground friction 8, braking friction 0 with separate friction disabled, friction factor 2, air control 0.05, falling lateral friction 0 and jump velocity 420 cm/s. Velocity is not zeroed.

## Regression and reload

Both subjects passed all 14 native cases: stationary jump, walking jump, running jump, repeated run-jump-run, held-forward jump, released-forward-in-air jump, idle, W walk, Shift+W run, S/A/D and both mouse axes. Jump/fall/land, possession, unit actor/component/root scales, native pose advancement, stature and placement were checked. Stationary landing lasts approximately 0.87 s with zero horizontal movement. Moving cases have no selected stationary landing hold. No horizontal teleport, non-finite pose, scale collapse or elevated-placement regression was detected.

Fresh-process reload passed. Runtime closure contains 31 packages for Female and 39 for Aegis, all within the previously certified destination closure plus the four isolated review packages per subject. No Manny/Quinn, John/Jane, retarget, source or authoring dependency was added. No animations were rebaked.

## Exact new assets

Under `/Game/MetaHumanTo3DCharacter/ReviewFixes/RunJumpLand/Female/`:

- `ABP_FemaleBodyMovementReview`
- `BP_FemaleBodyMovementReviewCharacter`
- `BP_FemaleBodyMovementReviewGameMode`
- `L_FemaleBodyMovementReview`

Under `/Game/MetaHumanTo3DCharacter/ReviewFixes/RunJumpLand/Aegis/`:

- `ABP_AegisMovementReview`
- `BP_AegisMovementReviewCharacter`
- `BP_AegisMovementReviewGameMode`
- `L_AegisMovementReview`

The corresponding files are under `Content/MetaHumanTo3DCharacter/ReviewFixes/RunJumpLand/`. Isolated authoring/measurement/check scripts are under `Working/ReviewFixes/RunJumpLand/`. Exact asset/file hashes and paths are in [result.json](result.json).

## Preservation and evidence

[Preservation audit](preservation_audit.json): **46,046 protected files**, zero changed, zero missing. Both authoritative 89-animation libraries are individually hash-checked unchanged. Accepted R1–R4 assets/scripts, original sources, Female/Aegis originals and John/Jane evidence are preserved. One pre-existing interactive runtime log appended with its original prefix intact. Git HEAD, index and pre-existing tracked status are unchanged; nothing was staged, committed or pushed.

[Native graph/clip inspection](inspection.json), [fresh reload/self-review](fresh_validation.json), [final checks](result.json), and `{Female,Aegis}_{before,after}_native.json` contain detailed trajectories, sequence-player times and observations. Native touchdown PNGs are retained. Harness API failures and the isolated graph-authoring commandlet crash remain in attempt reports/logs; fresh validation is the authoritative final asset receipt. No protected asset was saved by those attempts.

## Human review handoff

Female Editor PID **31604** remains open with:

`/Game/MetaHumanTo3DCharacter/ReviewFixes/RunJumpLand/Female/L_FemaleBodyMovementReview`

Native UE API confirmed useful editor camera, level loaded, PIE stopped and ready to press Play. Press **Play → Shift + W → Space**, continue forward and inspect the return to run. WASD, mouse, Shift and Space remain available.

Native UE captures and pose evidence were inspected. The desktop capture helper failed sandbox startup, so no separate desktop-window capture or continuous subjective motion approval is claimed. Andre's final hands-on judgement remains pending. Work stops here.
