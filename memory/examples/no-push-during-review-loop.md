---
name: no-push-during-review-loop
description: "Never push to a PR branch while a review-loop round is still running, push once when the loop is done"
metadata:
  type: feedback
---

Do not push to a PR branch while an automated review round is still
running. Push once, at the end of the review loop.

**Why:** the pushed state can change again after the round, so a human
reviewer who is already assigned sees churn.

**How to apply:** batch all review-loop fixes locally. When a human
review has started, land them as `fixup!` commits (see
[[force-push-feature-branches-ok]]), but push them only after the last
round reports. Amend and force-push only when no human review has
started.
