"""
cross-border-commerce-skill: Client SDK
Handle multi-currency conversion, import duties, and international shipping costs.
"""
from __future__ import annotations
from typing import Optional

# Exchange rates vs USD (approximate, for offline use)
FX_RATES = {
    "GB": ("GBP", 0.79), "DE": ("EUR", 0.92), "FR": ("EUR", 0.92),
    "JP": ("JPY", 157.0), "AU": ("AUD", 1.54), "CA": ("CAD", 1.37),
    "SG": ("SGD", 1.35), "TH": ("THB", 36.5), "KR": ("KRW", 1350.0),
    "CN": ("CNY", 7.25), "IN": ("INR", 83.5), "BR": ("BRL", 5.10),
    "MX": ("MXN", 17.2), "AE": ("AED", 3.67), "SA": ("SAR", 3.75),
    "NZ": ("NZD", 1.65), "CH": ("CHF", 0.90), "SE": ("SEK", 10.5),
    "NO": ("NOK", 10.8), "DK": ("DKK", 6.90),
}

# VAT/GST rates by country
VAT_RATES = {
    "GB": 0.20, "DE": 0.19, "FR": 0.20, "AU": 0.10, "NZ": 0.15,
    "CA": 0.05, "JP": 0.10, "SG": 0.09, "TH": 0.07, "KR": 0.10,
    "CH": 0.077, "SE": 0.25, "NO": 0.25, "DK": 0.25,
    "CN": 0.13, "IN": 0.18, "BR": 0.17, "MX": 0.16, "AE": 0.05,
    "SA": 0.15,
}

# Duty rates by category (%) -- simplified HS code averages
DUTY_RATES = {
    "beauty":     {"GB": 0.0, "DE": 0.0, "AU": 0.0, "JP": 3.0, "CA": 0.0, "CN": 5.0},
    "electronics":{"GB": 0.0, "DE": 0.0, "AU": 0.0, "JP": 0.0, "CA": 0.0, "CN": 10.0},
    "clothing":   {"GB": 12.0, "DE": 12.0, "AU": 5.0, "JP": 9.1, "CA": 18.0, "CN": 14.0},
    "footwear":   {"GB": 3.0, "DE": 3.0, "AU": 0.0, "JP": 15.0, "CA": 18.0, "CN": 24.0},
    "food":       {"GB": 0.0, "DE": 0.0, "AU": 0.0, "JP": 10.0, "CA": 7.5, "CN": 10.0},
    "toys":       {"GB": 0.0, "DE": 0.0, "AU": 0.0, "JP": 0.0, "CA": 0.0, "CN": 10.0},
    "furniture":  {"GB": 0.0, "DE": 0.0, "AU": 5.0, "JP": 0.0, "CA": 0.0, "CN": 12.0},
    "default":    {"GB": 3.5, "DE": 3.5, "AU": 2.5, "JP": 4.0, "CA": 4.0, "CN": 8.0},
}

# De minimis thresholds (USD) -- shipments below exempt from duty
DE_MINIMIS = {
    "US": 800, "CA": 20, "GB": 150, "AU": 1000, "NZ": 60,
    "JP": 16000, "SG": 400, "DE": 150, "FR": 150,
}

# Shipping costs (USD) by method and weight band
SHIPPING_RATES = {
    "economy":  {"base": 5.0, "per_kg": 3.5, "days": "14-21 business days"},
    "standard": {"base": 12.0, "per_kg": 6.0, "days": "7-10 business days"},
    "express":  {"base": 25.0, "per_kg": 12.0, "days": "2-4 business days"},
}

COMPLIANCE_NOTES = {
    "GB": ["UKCA marking required for electronics", "Customs declarations mandatory post-Brexit"],
    "DE": ["CE marking required for electronics", "Extended producer responsibility (EPR) registration for packaging"],
    "JP": ["PSE mark required for electrical appliances", "Japanese labeling regulations apply"],
    "AU": ["Australian Consumer Law refund rights apply", "Prohibited: certain agricultural products"],
    "CA": ["Bilingual (EN/FR) labeling required", "CRTC compliance for electronics"],
    "CN": ["CCC certification required for many electronics", "GB standard labeling required"],
    "BR": ["INMETRO certification required", "Import licenses may be needed for certain goods"],
    "IN": ["BIS certification required for electronics", "FSSAI approval for food products"],
    "SA": ["SASO certification for electronics", "Halal certification for food"],
    "AE": ["ESMA conformity for certain products", "Arabic labeling required"],
}


class CrossBorderClient:
    """
    SDK for cross-border e-commerce calculations.
    Covers currency conversion, duty estimation, shipping costs, and compliance notes.
    """

    def calculate(
        self,
        order_value_usd: float,
        destination_country: str,
        product_category: str = "default",
        weight_kg: float = 0.5,
        shipping_method: str = "standard",
    ) -> dict:
        """
        Calculate full landed cost for an international order.

        Args:
            order_value_usd:      Order value in USD.
            destination_country:  ISO 2-letter country code.
            product_category:     Product category for duty lookup.
            weight_kg:            Package weight in kg.
            shipping_method:      'economy', 'standard', or 'express'.

        Returns:
            dict with local_price, duties, shipping, total_landed_cost, compliance_notes
        """
        country = destination_country.upper()

        # Currency conversion
        currency, rate = FX_RATES.get(country, ("USD", 1.0))
        local_price = round(order_value_usd * rate, 2)

        # De minimis check
        de_min = DE_MINIMIS.get(country, 150)
        duty_exempt = order_value_usd <= de_min

        # Duties
        duty_rate = 0.0
        if not duty_exempt:
            cat_rates = DUTY_RATES.get(product_category.lower(), DUTY_RATES["default"])
            duty_rate = cat_rates.get(country, cat_rates.get("default", 3.5))

        duty_usd = round(order_value_usd * duty_rate / 100, 2)

        # VAT/GST
        vat_rate = VAT_RATES.get(country, 0.0)
        vat_base = order_value_usd + duty_usd
        vat_usd = round(vat_base * vat_rate, 2)

        total_duties_usd = duty_usd + vat_usd

        # Shipping
        ship_config = SHIPPING_RATES.get(shipping_method, SHIPPING_RATES["standard"])
        shipping_usd = round(ship_config["base"] + weight_kg * ship_config["per_kg"], 2)

        # Total landed cost
        landed_cost_usd = round(order_value_usd + total_duties_usd + shipping_usd, 2)
        landed_cost_local = round(landed_cost_usd * rate, 2)

        duties_obj = {
            "duty_rate_pct": duty_rate,
            "duty_usd": duty_usd,
            "vat_gst_rate_pct": round(vat_rate * 100, 1),
            "vat_gst_usd": vat_usd,
            "total_duties_usd": total_duties_usd,
            "duty_exempt": duty_exempt,
            "de_minimis_threshold_usd": de_min,
        }

        shipping_obj = {
            "method": shipping_method,
            "cost_usd": shipping_usd,
            "estimated_transit": ship_config["days"],
            "weight_kg": weight_kg,
        }

        return {
            "destination_country": country,
            "product_category": product_category,
            "order_value_usd": order_value_usd,
            "local_price": {"currency": currency, "amount": local_price, "rate_vs_usd": rate},
            "duties": duties_obj,
            "shipping": shipping_obj,
            "total_landed_cost_usd": landed_cost_usd,
            "total_landed_cost_local": {"currency": currency, "amount": landed_cost_local},
            "duties_as_pct_of_order": round(total_duties_usd / max(order_value_usd, 1) * 100, 1),
            "compliance_notes": COMPLIANCE_NOTES.get(country, ["No specific compliance notes available."]),
        }

    def compare_countries(
        self,
        order_value_usd: float,
        countries: list[str],
        product_category: str = "default",
        weight_kg: float = 0.5,
        shipping_method: str = "standard",
    ) -> list[dict]:
        """Compare landed costs across multiple destination countries."""
        results = []
        for country in countries:
            result = self.calculate(order_value_usd, country, product_category, weight_kg, shipping_method)
            results.append({
                "country": result["destination_country"],
                "currency": result["local_price"]["currency"],
                "local_price": result["local_price"]["amount"],
                "total_duties_usd": result["duties"]["total_duties_usd"],
                "shipping_usd": result["shipping"]["cost_usd"],
                "landed_cost_usd": result["total_landed_cost_usd"],
                "duties_pct": result["duties_as_pct_of_order"],
                "duty_exempt": result["duties"]["duty_exempt"],
            })
        results.sort(key=lambda x: x["landed_cost_usd"])
        return results
