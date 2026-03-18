# Insights

## Insight 1 — AmbroseValley is the Most Popular Map

### What I Observed
AmbroseValley has significantly more matches and player files than GrandRift and Lockdown combined across all 5 days of data.

### Supporting Data
- February 10 alone has 437 files majority on AmbroseValley
- GrandRift and Lockdown have significantly fewer matches per day

### Why It Matters for a Level Designer
The most played map needs the most attention. If players keep choosing AmbroseValley it means either the other maps have problems or AmbroseValley has something special worth studying and replicating.

### Actionable Recommendation
Analyze what makes AmbroseValley more popular and apply those design principles to GrandRift and Lockdown to balance player distribution across maps.

---

## Insight 2 — Bots Die More to Storm Than Humans

### What I Observed
Looking at KilledByStorm events — bots have a higher rate of storm deaths compared to human players suggesting bots do not navigate away from the storm as effectively as humans.

### Supporting Data
Filtering by KilledByStorm events in the heatmap shows bot deaths clustered near storm boundaries while human deaths are more spread across the map.

### Why It Matters for a Level Designer
If bots are dying to the storm too frequently it means the bot AI pathing is not responding well to storm movement. This affects game balance because matches end too quickly.

### Actionable Recommendation
Review bot AI pathfinding logic near storm boundaries and add extraction routes that guide bots away from storm zones more effectively.

---

## Insight 3 — High Traffic Zones Are Concentrated in Center of Map

### What I Observed
The All Traffic heatmap on AmbroseValley shows player movement is heavily concentrated in the center of the map with edges and corners rarely visited.

### Supporting Data
Heatmap visualization clearly shows hot zones in central areas and cold zones near map edges across multiple matches and dates.

### Why It Matters for a Level Designer
If players only use 40-50% of the map the level designer has wasted effort building the rest. It also creates unfair chokepoints where all combat happens in the same spots.

### Actionable Recommendation
Add high value loot or objectives in undervisited areas to incentivize players to explore the full map and reduce central chokepoint congestion.