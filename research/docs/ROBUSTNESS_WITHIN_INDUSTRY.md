# Robustness of the within-industry GVA finding

`research/scripts/robustness_within_industry.py` tests whether Tamil Nadu's lower ASI GVA per person engaged under a common broad-industry composition could be an artifact of industry mix, classification granularity, one unusual year, or capital intensity. The script is read-only. It does not change the payload or the method.

## Summary of the finding

As a descriptive claim about ASI 2023-24, the finding holds across the specifications tested. The within-industry component is the majority of the GVA-per-person-engaged gap against India, Gujarat, Maharashtra and Karnataka in every specification tested (54-86%). The gap is broad-based across industries rather than driven by any single one. The complete panel shows the same sign for sixteen consecutive years. This is not evidence for a causal or efficiency interpretation.

The following remain unmeasured:

- composition below the 2-digit industry level (product mix inside an industry);
- price and deflator differences across states, since all values are at current prices;
- design-based uncertainty on the decompositions. ASI publishes no state-level RSEs, so none are computed;
- the reasons for the gap. The analysis is cross-sectional and has no causal design.

The site describes the finding as "is associated with less value added within the same industries." The limits above apply to that wording.

## (a) Classification-granularity sensitivity

The symmetric Kitagawa decomposition of the ASI GVA-per-person-engaged gap was re-run at 24 NIC 2-digit industries, the finest published granularity. True employment weights were recomputed from the raw frame. The script checks its output against the payload and stops if the maximum relative deviation exceeds `1e-12`. The publication run gave 0.0. Cells are restricted to jointly published (non-suppressed) payload cells. Employment coverage of the retained cells is 94.6-100%.

Within-component share of the common-support gap:

| Comparator | 7 groups (published) | 7×4 industry×size (published) | 24 NIC2 (this run) |
|---|---:|---:|---:|
| India | 75.6% | 67.5% | 65.4% |
| Gujarat | 67.2% | 55.8% | 54.0% |
| Maharashtra | 70.9% | 67.5% | 65.6% |
| Karnataka | 84.0% | 80.9% | 85.9% |
| Telangana | unstable: gap only about ₹38-46k, component shares not meaningful | | |
| Kerala | suppressed (Tamil Nadu coverage below 95%) | suppressed | Tamil Nadu above Kerala on common support |

Reading across specifications: industry mix explains between a seventh and a half of the gap, depending on the comparator and the granularity. The within-industry component is the majority in every specification against every major comparator. At NIC2 granularity the mix share reaches 46% against Gujarat, so the "a sixth to a third" range from the 7-group analysis does not hold across all specifications.

Breadth: Tamil Nadu's rate sits below the comparator's in 21 of 24 cells (India), 16 of 24 (Gujarat), 22 of 23 (Maharashtra) and 19 of 22 (Karnataka). These cells cover 74-97% of common-weight employment. The gap is not a one-industry pattern.

Kerala: Kerala's high aggregate GVA per worker is carried by cells outside common support (petroleum refining is suppressed for concentration). Within common support, Tamil Nadu is above Kerala in employment terms. The Tamil Nadu to Kerala adjusted row is suppressed in the payload, and this comparison is not reported as an adjusted row.

## (b) Multi-year persistence (ASI panel, 2008-2023)

The panel uses `-` where Tamil Nadu's value is lower, `+` where it is higher or equal, and `·` where either side is missing. An all-years conclusion is reported only when every required pair is observed.

For the complete all-manufacturing series (calibrated so that Tamil Nadu 2023 = 839,770, exactly as in the payload), Tamil Nadu is below Gujarat, Maharashtra and Karnataka in all sixteen years, 2008-2023. The 2023 ratios are 0.64, 0.55 and 0.56. Telangana has four missing early pairs, so no all-years conclusion is reported for it. Among the observed years its sign alternates, which is consistent with the small 2023-24 gap. Kerala: Tamil Nadu is above Kerala until 2010 and below since 2011 (see the refinery note in section (a)).

Named sectors, 2020-2023: Tamil Nadu is lower in all comparable years against Maharashtra in electrical-electronics, electronics-core, food-processing, leather-footwear, life-sciences and textiles-apparel. It is lower than Karnataka in five of those sectors and lower than Gujarat in food-processing, life-sciences and textiles-apparel. Tamil Nadu's clear strength is automobiles, where it is at or above every peer except Maharashtra. The 2023-24 finding is not a one-year artifact.

## (c) Capital intensity as a descriptive channel

Fixed capital per employee in 2023, Tamil Nadu as a ratio of each peer: all-manufacturing **0.36× Gujarat, 0.57× Maharashtra and 0.55× Karnataka**. Tamil Nadu's factories are markedly capital-shallow.

Within sectors the pattern varies. Textiles (0.61-0.76×), food processing (0.44-0.46×) and life sciences (0.63-0.74×) are less capital-intensive where they are less productive. There, low capital per worker is a plausible proximate channel for the GVA gap. Electrical-electronics runs more capital per employee than every peer (1.30-1.52× Gujarat, Maharashtra, Karnataka and Telangana) while producing 32-45% less value per person than those states. Electronics-core runs more capital than Gujarat, Maharashtra and Telangana (1.36-1.95×; Karnataka is the exception at 0.87×) while producing 39-43% less value than Maharashtra, Karnataka and Telangana, and roughly the same as Gujarat. Capital shallowness therefore does not account for the whole gap.

The site presents capital intensity as a descriptive channel: "Tamil Nadu's factories work with about a third of Gujarat's capital per person." It is not presented as a complete explanation.

## (d) Joint adjustment already published

The payload already publishes industry×size-adjusted rows (`broad_industry_7_x_common_size_4`) for all three ASI outcomes. The within-component survives joint adjustment for industry and factory size. These rows are in the payload, so no further computation is needed.

## Conclusion

Under a common broad-industry composition, a gap remains. It is the main component of the total gap in every specification tested. METHODOLOGY.md states the unmeasured factors and gives the range of the industry-mix share.
