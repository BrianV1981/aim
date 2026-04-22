# Q: Feature: Relocate background hook state files to hooks/.state/
**Source:** https://github.com/BrianV1981/aim/issues/291

## The Problem / Request
## Description
Feature: Relocate background hook state files to hooks/.state/

### 🧠 Commander's Intent
**Context:**
The background python hooks (failsafe snapshot and cognitive mantra) generate state-tracking databases (INTERIM_BACKUP.json and mantra_state.json). They were previously moved to continuity/private, but that is not the ideal semantic location.

**The Goal/Failure:**
'private' implies secrecy, but these are just machine state files. They should live close to the logic that operates on them.

**Action Items:**
1. Move INTERIM_BACKUP.json and mantra_state.json into a dedicated hooks/.state/ subfolder.
2. Update the Python hook scripts to point to the new location.
3. Remove the old continuity/private directory.

## The Solution / Discussion
### Response 1
This feature was successfully built and merged into main under commit `60db1bf` (the 'aim mail' integration) before the rollback occurred. Because the rollback only affected uncommitted files and the rogue branch, this cleanup remains perfectly intact. Closing ticket as already resolved.

