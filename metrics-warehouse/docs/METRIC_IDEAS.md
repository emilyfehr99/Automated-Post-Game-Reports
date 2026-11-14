# Metric ideas (next adds)

Grounded in what we already store (NHL PBP + LLD + InStat). Schema v3 shipped the prior high-value set.

## Shipped (schema v3)

1. Dump-in recovery %
2. Entry denial rate (proxy) + failed entries by lane/type
3. SC off dump vs carry
4. Zone turnover → shot against (OZ/NZ/DZ)
5. Slot drive → shot/SC/goal conversion
6. DZ retrieval → controlled exit %
7. Forecheck pressure composite
8. Carry-in % + battles_engaged aliases on InStat flat
9. Score-state splits (tied/leading/trailing)
10. Failed exits by lane/type + forced failed exits

## Still open / stretch

11. True puck battle win% by zone (needs InStat action PBP; gear has BRS volume only)
12. Rush chain length — events between possession change and rush SC
13. Goalie rebound diet — LLD rebound GSAx × opponent slot-drive rate
14. True positive/failed touches (InStat tags)
15. Royal road / east-west pre-shot on shooters (extend LLD `ewProxy`)
16. Line-level microstats (shifts API × on-ice events)
17. Period-1 vs period-3 transition fingerprint
18. Net-front screen rate on goals (sprites)
19. Goalie freeze vs uncontrolled by danger (InStat saveDetail)
