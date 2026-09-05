window.AU_CALC_CONFIG = {
  "fy": "2025-26",
  "last_checked": "2026-08-22",
  "gst_rate": 0.1,
  "medicare_levy": 0.02,
  "medicare_lower": 28011,
  "medicare_upper": 35013,
  "default_days": 220,
  "brackets": [
    {
      "up_to": 18200,
      "base": 0,
      "rate": 0.0
    },
    {
      "up_to": 45000,
      "base": 0,
      "rate": 0.16
    },
    {
      "up_to": 135000,
      "base": 4288,
      "rate": 0.3
    },
    {
      "up_to": 190000,
      "base": 31288,
      "rate": 0.37
    },
    {
      "up_to": null,
      "base": 51638,
      "rate": 0.45
    }
  ],
  "sources": [
    {
      "label": "ATO resident tax rates 2025-26",
      "url": "https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents/"
    },
    {
      "label": "ATO Medicare levy reduction (low-income thresholds)",
      "url": "https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners"
    },
    {
      "label": "GST rate (10%) - ATO GST overview",
      "url": "https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst"
    }
  ],
  "formspree_endpoint": "https://formspree.io/f/YOUR_FORM_ID",
  "site_name": "AU Freelancer Calc",
  "site_tagline": "Day rate to annual to take-home (AU contractor estimate)",
  "base_url": "https://au-freelancer-calc-e23a.surge.sh"
};
