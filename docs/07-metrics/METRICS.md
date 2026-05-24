# Metrics: Real Estate Permits MCP

## Purpose

Define what success looks like at each product stage. Metrics should be measurable, tied to user value, and few enough to actually track.

---

## Prototype Metrics (Current Stage)

These measure whether the tool works reliably enough to hand to someone else.

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Query success rate | >95% | % of tool calls that return data (vs. error) over 30 days |
| Response latency (p50) | <3 seconds | Time from tool call to response, measured via httpx timing |
| Response latency (p90) | <8 seconds | Same, 90th percentile |
| Use case completion rate | 3/3 proven use cases work | Manual testing: UC-01, UC-02, UC-03 end-to-end |
| Setup success (non-author) | 1 person succeeds | One person follows README and gets working results |

**Not tracking yet:** User count, feature adoption, retention. Too early — single user.

---

## Beta Metrics

These measure whether real users find the tool valuable.

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Active users | 3-5 | Users who make at least 1 query in a 2-week period |
| Time-to-first-value | <30 minutes | Time from git clone to first successful query (self-reported + README clarity) |
| Query success rate | >90% across users | Aggregate across all beta users (API errors + bad input) |
| Setup completion rate | >75% | % of people who attempt setup and succeed |
| NPS or satisfaction | >7/10 | Simple survey: "How likely are you to recommend this tool?" |
| Bug reports | Tracked | GitHub Issues opened during beta |
| Feature requests | Tracked | GitHub Issues labeled as enhancement |

**Key Qualitative Metric:** Can a beta user explain what the tool does to someone else in one sentence? If not, the narrative needs work.

---

## V1 Release Metrics

These measure whether the product has found sustainable traction.

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Monthly active users | 10+ | Users making queries in a calendar month |
| GitHub stars | 50+ | Vanity, but proxy for awareness |
| Organic installs | 5+/month | Installs not driven by direct outreach |
| Data accuracy complaints | <2/month | Issues reporting incorrect data |
| Documentation sufficiency | >90% self-serve | % of users who set up without asking for help |

---

## Business Viability Metrics (Post-V1)

Only relevant if pursuing monetization. Track if and when that decision is made.

| Metric | Definition |
|--------|-----------|
| Willingness to pay | % of users who say they'd pay for a pro tier (survey) |
| Price sensitivity | Acceptable price range from user interviews |
| Cost to serve | API costs + hosting per user per month |
| Retention (30-day) | % of new users still active after 30 days |
| Revenue (if applicable) | Monthly recurring revenue |

---

## Anti-Metrics (Things NOT to Optimize For)

| Anti-Metric | Why |
|------------|-----|
| Total queries | More queries ≠ more value. A user who gets their answer in 1 query is better served than one who needs 10. |
| Feature count | More tools ≠ better product. Prefer fewer, more reliable tools. |
| Geographic coverage | More cities ≠ better product (yet). Depth in Seattle beats breadth across 10 cities with shallow support. |
| Speed at the expense of accuracy | A fast wrong answer is worse than a slow correct one. |

---

## Measurement Infrastructure

**Current (Prototype):** No automated measurement. Manual observation.

**Beta:** Add lightweight logging to the MCP server — log tool name, latency, success/failure, and timestamp. Store locally in a JSONL file. No PII, no query content, just operational metrics.

**V1:** Consider opt-in telemetry (with clear disclosure) if user count justifies the investment. Otherwise, continue with GitHub Issues + manual feedback as the primary signal.
