"""
example_usage.py -- Demonstrates the CrossBorderClient SDK.
"""
from client import CrossBorderClient

def main():
    client = CrossBorderClient()

    print("[1] Single Order Landed Cost Calculation")
    result = client.calculate(
        order_value_usd=89.99,
        destination_country="DE",
        product_category="beauty",
        weight_kg=0.4,
        shipping_method="standard",
    )
    lp = result["local_price"]
    d = result["duties"]
    s = result["shipping"]
    print(f"Order: ${result['order_value_usd']} USD -> {lp['currency']} {lp['amount']:.2f} (rate: {lp['rate_vs_usd']})")
    print(f"Duty: {d['duty_rate_pct']}% = ${d['duty_usd']} | VAT: {d['vat_gst_rate_pct']}% = ${d['vat_gst_usd']}")
    print(f"Duty Exempt: {d['duty_exempt']} (de minimis ${d['de_minimis_threshold_usd']})")
    print(f"Shipping ({s['method']}): ${s['cost_usd']} | Transit: {s['estimated_transit']}")
    print(f"TOTAL LANDED COST: ${result['total_landed_cost_usd']} USD / {lp['currency']} {result['total_landed_cost_local']['amount']:.2f}")
    print(f"Duties as % of order: {result['duties_as_pct_of_order']}%")
    print(f"Compliance Notes:")
    for note in result["compliance_notes"]:
        print(f"  - {note}")

    print("\n[2] Country Comparison -- Where to sell?")
    comparison = client.compare_countries(
        order_value_usd=50.00,
        countries=["GB", "DE", "AU", "JP", "CA", "SG"],
        product_category="beauty",
        shipping_method="standard",
    )
    print(f"{'Country':<8} {'Currency':<8} {'Local Price':>12} {'Duties USD':>12} {'Shipping':>10} {'Landed USD':>12} {'Duty %':>8}")
    for c in comparison:
        print(f"{c['country']:<8} {c['currency']:<8} {c['local_price']:>12.2f} {c['total_duties_usd']:>12.2f} {c['shipping_usd']:>10.2f} {c['landed_cost_usd']:>12.2f} {c['duties_pct']:>7.1f}%")

if __name__ == "__main__":
    main()
