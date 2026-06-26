# Venue Procurement Ground Truth

## Rules
1. Capacity must appear in extracted page text — never invent capacity.
2. Stated capacity must be >= brief headcount when headcount is specified.
3. Total venue price must be <= user budget when price is extractable.
4. If brief requires natural light, page text should mention light/windows/daylight.
5. Trusted domains: tagvenue.com, venuescanner.com, hirespace.com, headbox.com.

## Verification
- grounded=true if capacity in extract AND capacity >= headcount AND price <= budget (when both known)
- Flag "capacity_not_in_extract" if capacity missing
- Flag "under_capacity" if capacity < required headcount
- Flag "over_budget" if price > budget
