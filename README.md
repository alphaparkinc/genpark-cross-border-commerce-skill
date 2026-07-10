# genpark-cross-border-commerce-skill

> **GenPark AI Agent Skill** -- Handle cross-border e-commerce: multi-currency conversion, import duties, shipping costs, and compliance checks.

## Features

- Currency conversion for 20+ countries (offline FX rates)
- Import duty rates by product category and destination
- VAT/GST calculation per country
- De minimis threshold check (duty exemption)
- Shipping cost by method (economy/standard/express) and weight
- Full landed cost calculation
- Country compliance notes
- Multi-country comparison mode

## Quick Start

```python
from client import CrossBorderClient

client = CrossBorderClient()
result = client.calculate(
    order_value_usd=89.99,
    destination_country="GB",
    product_category="clothing",
    weight_kg=0.5,
    shipping_method="standard",
)
print(f"Landed cost: ${result['total_landed_cost_usd']}")
print(f"Local price: {result['local_price']['currency']} {result['local_price']['amount']}")
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
