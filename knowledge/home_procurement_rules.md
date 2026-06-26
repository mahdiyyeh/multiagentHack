# Home Procurement Ground Truth

## Rules
1. Price must appear verbatim in extracted page text — never invent prices.
2. Total item price must be <= user budget.
3. Prefer listings with in-stock signals: "add to basket", "in stock", "buy now".
4. Reject candidates with no extractable price.
5. Trusted retailer domains: ikea.com, amazon.co.uk, wayfair.co.uk, johnlewis.com, argos.co.uk.

## Verification
- grounded=true only if price found in raw_extract AND price <= budget
- Flag issue "price_not_in_extract" if price not in page text
- Flag issue "over_budget" if price exceeds budget
