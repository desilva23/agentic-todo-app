# Data Model: Console Look

This feature changes only how existing information is shown. It adds, removes and changes **no data**: no new fields,
no new storage, no change to the todo, the assistant's preview, suggestion or reminder shapes (see features 001 and
002). Nothing is persisted by this feature.

The only "model" is the set of visible labels the page builds from existing fields:

| Shown as | Built from | Rule |
|---|---|---|
| `[high]` `[medium]` `[low]` | the todo's priority | the word in brackets |
| `[active]` `[completed]` | the todo's status | the word in brackets |
| `[overdue]` `[due soon]` | the assistant's reminder items (`overdue` true or false) | the word in brackets |
