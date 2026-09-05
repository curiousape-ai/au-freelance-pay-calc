window.AU_CALC_CONFIG = {
  "default_fy": "2026-27",
  "years": {
    "2025-26": {
      "last_checked": "2026-09-05",
      "medicare_levy": 0.02,
      "medicare_lower": 28011,
      "medicare_upper": 35013,
      "medicare_note": "FY2025-26 single thresholds.",
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
      "help": {
        "threshold": 67000,
        "upper_threshold": 125000,
        "lower_rate": 0.15,
        "upper_rate": 0.17,
        "cap_rate": 0.1
      }
    },
    "2026-27": {
      "last_checked": "2026-09-05",
      "medicare_levy": 0.02,
      "medicare_lower": 28011,
      "medicare_upper": 35013,
      "medicare_note": "ATO has not published a separate FY2026-27 single threshold pair; FY2025-26 thresholds are retained.",
      "brackets": [
        {
          "up_to": 18200,
          "base": 0,
          "rate": 0.0
        },
        {
          "up_to": 45000,
          "base": 0,
          "rate": 0.15
        },
        {
          "up_to": 135000,
          "base": 4020,
          "rate": 0.3
        },
        {
          "up_to": 190000,
          "base": 31020,
          "rate": 0.37
        },
        {
          "up_to": null,
          "base": 51370,
          "rate": 0.45
        }
      ],
      "help": {
        "threshold": 69528,
        "upper_threshold": 129717,
        "lower_rate": 0.15,
        "upper_rate": 0.17,
        "cap_rate": 0.1
      }
    }
  },
  "gst_rate": 0.1,
  "sg_rate": 0.12,
  "gst_registration_threshold": 75000,
  "default_days": 220,
  "default_hours_per_day": 8,
  "sources": [
    {
      "label": "Australian resident income tax rates",
      "url": "https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents/individual-income-tax-rates"
    },
    {
      "label": "Medicare levy reduction for low-income earners",
      "url": "https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners"
    },
    {
      "label": "Study and training loan repayment thresholds",
      "url": "https://www.ato.gov.au/tax-rates-and-codes/study-and-training-support-loans-rates-and-repayment-thresholds"
    },
    {
      "label": "GST overview",
      "url": "https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst"
    }
  ],
  "site_name": "AU Freelancer Calc",
  "site_tagline": "Day rate to annual to take-home (AU contractor estimate)",
  "base_url": "https://au-freelance-pay-calc.netlify.app",
  "author": {
    "name": "Ian Hunt",
    "url": "https://curiousape.au/",
    "same_as": [
      "https://curiousape.au/",
      "https://www.linkedin.com/in/ijhunt/"
    ]
  },
  "publisher": {
    "name": "Curious Ape",
    "url": "https://curiousape.au/",
    "same_as": [
      "https://curiousape.au/"
    ]
  },
  "analytics_domain": "au-freelance-pay-calc.netlify.app"
};
