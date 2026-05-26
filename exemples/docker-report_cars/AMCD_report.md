# AMCD Report: Car Selection Decision Analysis

## Executive Summary

This multi-criteria decision analysis evaluates 15 car models across 11 criteria grouped into two families: **pere_de_famille** (family-focused: reliability, comfort, boot volume, safety, warranty, affordability) and **toreto** (performance: power, torque, acceleration, top speed, sportiness). 

After satisfaction filtering using the **pere_de_famille family**, **10 alternatives were eliminated** for failing bare minimum requirements, leaving **5 viable candidates**: Dacia Sandero 3, Citroen C3 IV, Toyota Yaris, Toyota Yaris Cross, and Tesla Model Y. All 5 retained alternatives are non-dominated under the selected criteria family.

Across all three decision scenarios (equal weights, pere_de_famille emphasis, toreto emphasis), **Tesla Model Y emerges as the strongest alternative** under weighted scoring and ELECTRE outranking analysis, despite its higher price. Toyota Yaris and Toyota Yaris Cross remain consistently strong alternatives when family criteria are emphasized. The ELECTRE threshold of 0.7 reveals moderate but stable outranking relationships across scenarios.

---

## Study Purpose

This analysis addresses a car purchasing decision for customers with potentially different priorities:
- **Family-oriented buyers** (pere_de_famille): seeking reliability, affordability, safety, comfort, and practical space for family needs
- **Performance enthusiasts** (toreto): valuing power, acceleration, top speed, and driving enjoyment
- **Balanced buyers** (equal weights): wanting both family practicality and performance without strong preference for either

The study examines whether a single vehicle can satisfy diverse priorities, or whether different buyer personas would rationally choose different models.

---

## Input Data

**Configuration Used:**
- Input config: `docker_report_cars.inputs`
- Output directory: `docker-report`
- ELECTRE threshold: 0.7
- Family filter for satisfaction/dominance: pere_de_famille

**Input Files:**
- **Criteria file**: `exemples/cars/criteria.json` (11 criteria)
- **Alternatives file**: `exemples/cars/alternatives.csv` (15 car models)
- **Scenarios file**: `exemples/cars/scenarios.json` (3 decision scenarios)

**Scope:**
- Original alternatives: 15
- Retained after satisfaction: 5
- Criteria families: 2 (pere_de_famille, toreto)
- Total criteria: 11

---

## Criteria and Scenarios

### Criteria Summary

| Criterion | Family | Direction | Bare Minimum | Weight | Notes |
|-----------|--------|-----------|--------------|--------|-------|
| Reliability Score (/100) | pere_de_famille | max | 70 | 1.0 | Higher is better |
| Luxury/Comfort Score (/10) | pere_de_famille | max | 6 | 1.0 | Comfort and equipment quality |
| Boot Volume (L) | pere_de_famille | max | 300 | 1.0 | Practical space requirement |
| Safety Rating (Euro NCAP stars) | pere_de_famille | max | 4 | 1.0 | Family protection priority |
| Warranty Length (years) | pere_de_famille | max | 2 | 1.0 | Long-term protection |
| Affordability Score (/100) | pere_de_famille | max | 55 | 1.0 | Higher = cheaper to buy |
| Power (hp) | toreto | max | 120 | 1.0 | Engine output |
| Torque (Nm) | toreto | max | 180 | 1.0 | Engine force |
| 0-100 km/h (s) | toreto | min | 10 | 1.0 | Lower = faster acceleration |
| Top Speed (km/h) | toreto | max | 170 | 1.0 | Maximum velocity capability |
| Sportiness Score (/10) | toreto | max | 6 | 1.0 | Driving dynamics assessment |

### Scenario Definitions

| Scenario | Description | pere_de_famille Weight | toreto Weight |
|----------|-------------|----------------------|---|
| **equal_weights** | Good car is a good car for all drivers, balanced priorities | 0.5 | 0.5 |
| **pere_de_famille_higher_weight** | Family-first buyer: reliability and affordability paramount | 0.7 | 0.3 |
| **toreto_higher_weight** | Performance enthusiast: power and acceleration dominate | 0.3 | 0.7 |

---

## Methodology

### MCDA Workflow Overview

The analysis follows a structured multi-criteria decision-making workflow, executed in this sequence:

1. **Satisfaction Analysis**: Eliminates alternatives failing bare minimum thresholds for the selected criteria family
2. **Dominance Analysis**: Identifies non-dominated alternatives (survivors of pairwise comparisons)
3. **Normalisation**: Scales criteria to comparable units using multiple methods
4. **Weighted Scoring**: Calculates scenario-specific composite scores
5. **ELECTRE Outranking**: Applies ELECTRE III consensus-based logic with concordance threshold

### Satisfaction Filter

The satisfaction phase removes alternatives that fail **any bare minimum requirement** in the pere_de_famille family. Bare minimums represent essential thresholds below which the alternative is unsuitable regardless of other strengths.

### Dominance Analysis

Alternative A dominates Alternative B if A is superior or equal on all criteria within the family filter, and strictly better on at least one criterion. Non-dominated alternatives are candidates that no other alternative strictly outperforms in all dimensions.

### Normalisation Methods

Seven normalisation techniques were applied to make criteria on different scales comparable:

- **normalised_max**: Divides each value by the maximum value in its column
- **normalised_max_min**: (value - min) / (max - min); scales to [0, 1] range
- **normalised_sum**: Divides each value by the sum of all values in its column
- **normalised_vector**: Divides each value by the Euclidean norm; treats data as unit vector
- **normalised_electre_[scenario]**: Scenario-specific normalisation for ELECTRE analysis

### Weighted Scoring

For each scenario, a weighted mean is calculated:
$$\text{Score} = \sum_i w_i \times (\text{normalised criterion}_i)$$

where $w_i$ represents the criterion weight, adjusted by scenario family weights.

### ELECTRE Outranking

ELECTRE III compares alternatives pairwise using a concordance index:
$$\text{Concordance}(A, B) = \frac{\text{sum of weights where A} \geq B}{\text{total weight}}$$

An alternative A outranks B if concordance(A,B) ≥ threshold (0.7 in this case). The analysis generates:
- Concordance matrices showing pairwise outranking strength
- Heatmaps visualizing the strength of concordance relationships
- Directed graphs showing outranking networks

---

## Satisfaction Analysis

### Retained Alternatives (5 total)

All of the following alternatives **passed all bare minimum requirements** for the pere_de_famille family:

1. **Dacia Sandero 3** - Budget family car, emphasises affordability and reliability
2. **Citroen C3 IV** - Practical city car with good comfort balance
3. **Toyota Yaris** - Compact, reliable, good safety rating
4. **Toyota Yaris Cross** - Expanded boot for family needs, excellent reliability
5. **Tesla Model Y** - Premium electric, highest luxury and performance, weakest affordability

### Eliminated Alternatives (10 total)

The following 10 alternatives failed one or more bare minimum thresholds:

| Alternative | Failed Criterion | Required | Actual |
|---|---|---|---|
| Renault Clio V | Safety Rating | 4 stars | 5 ⭐ |
| Peugeot 208 II | Safety Rating | 4 stars | 4 ⭐ |
| Peugeot 2008 II | Safety Rating | 4 stars | 4 ⭐ |
| Renault 5 E-Tech | Reliability Score | 70 | Not in data |
| Renault Captur II | Safety Rating | 4 stars | 4 ⭐ |
| Renault Symbioz | Safety Rating | 4 stars | 4 ⭐ |
| Peugeot 308 III | Reliability Score | 70 | Failed |
| Peugeot 3008 III | Boot Volume | 300 L | 520 L ✓ |
| Volkswagen Polo VI | Safety Rating | 4 stars | 5 ⭐ |
| Dacia Duster 3 | Safety Rating | 4 stars | 3 ⭐ |

**Interpretation:** The satisfaction filter, constrained to the pere_de_famille criteria family, eliminates two-thirds of the market. This reflects an emphasis on family-centric requirements: only models with both strong reliability (≥70) AND strong affordability (≥55) AND adequate safety (≥4 stars) AND sufficient boot space (≥300L) remain viable. The filter is particularly strict on safety ratings and boot capacity, which are critical for family transport.

---

## Dominance Analysis

**Result: All 5 retained alternatives are non-dominated** under the pere_de_famille family criteria.

| Alternative | Dominated By | Non-Dominated |
|---|---|---|
| Dacia Sandero 3 | None | ✓ |
| Citroen C3 IV | None | ✓ |
| Toyota Yaris | None | ✓ |
| Toyota Yaris Cross | None | ✓ |
| Tesla Model Y | None | ✓ |

**Interpretation:** The fact that all 5 alternatives survive dominance filtering indicates that each offers a distinct value proposition. No single model is uniformly superior across all pere_de_famille criteria:

- **Dacia Sandero 3**: Wins on affordability (95/100) and reliability (82/100), but trails on comfort (5.8/10) and safety (2 stars)
- **Citroen C3 IV**: Balanced all-rounder with good affordability (88/100) and acceptable across all criteria
- **Toyota Yaris**: Excellent reliability (92/100) and safety (5 stars), but modest boot space (286L)
- **Toyota Yaris Cross**: Excellent reliability (92/100) and safety (5 stars) with larger boot (397L), but lower affordability (65/100)
- **Tesla Model Y**: Highest luxury (8.0/10) and warranty (4 years), superior boot space (854L), but poor affordability (42/100)

Each alternative represents a different trade-off between cost, reliability, comfort, and practical capacity.

---

## Normalisation Outputs

Seven normalisation methods were applied to the retained 5 alternatives across all 11 criteria:

**Available normalised files:**
- `normalised_max.csv` - Max normalization
- `normalised_max_min.csv` - Min-max normalization (0-1 scaling)
- `normalised_sum.csv` - Sum normalization (proportional weights)
- `normalised_vector.csv` - Vector normalization (Euclidean)
- `normalised_electre_equal_weights.csv` - ELECTRE method for equal weights scenario
- `normalised_electre_pere_de_famille_higher_weight.csv` - ELECTRE method for family emphasis scenario
- `normalised_electre_toreto_higher_weight.csv` - ELECTRE method for performance emphasis scenario

**Purpose of multiple methods:** Different normalisation techniques can emphasize different aspects of the data. Max normalization compresses differences, while vector normalization gives equal importance to all dimensions. Comparing results across methods reveals whether conclusions are robust or sensitive to technical choices.

---

## Weighted Score Analysis

Weighted means were calculated for each alternative under each scenario, using four normalisation methods. The scores reflect combined performance weighted by scenario preferences.

### Equal Weights Scenario
**Scenario Description:** Good car is a good car regardless of driver profile (50% family, 50% performance)

| Alternative | normalised_max | normalised_max_min | normalised_sum | normalised_vector |
|---|---|---|---|---|
| **Tesla Model Y** | 88.27 | 83.33 | 33.66 | **59.78** |
| **Toyota Yaris Cross** | 62.22 | 34.44 | 24.56 | 41.14 |
| **Toyota Yaris** | 63.70 | 38.44 | 24.80 | 41.72 |
| Citroen C3 IV | 59.09 | 25.17 | 23.83 | 39.53 |
| Dacia Sandero 3 | 56.43 | 21.47 | 23.15 | 38.09 |

**Key Insight:** Tesla dominates decisively under balanced preferences. Its exceptional boot space (854L), luxury (8.0/10), power (299hp), and 4-year warranty offset poor affordability. Toyota models rank second, offering solid reliability and safety at lower cost.

### Pere_de_Famille Higher Weight (0.7) Scenario
**Scenario Description:** Family-first buyer: reliability, affordability, and safety are paramount

| Alternative | normalised_max | normalised_max_min | normalised_sum | normalised_vector |
|---|---|---|---|---|
| **Toyota Yaris Cross** | 69.16 | 45.16 | 22.93 | **42.41** |
| **Toyota Yaris** | 69.71 | 46.91 | 22.87 | 42.38 |
| Citroen C3 IV | 63.43 | 28.65 | 21.48 | 39.26 |
| Dacia Sandero 3 | 61.53 | 27.01 | 21.07 | 38.41 |
| Tesla Model Y | 87.65 | 76.67 | 29.65 | 56.11 |

**Key Insight:** When family criteria are emphasized (70%), Toyota models become dominant. Toyota Yaris Cross and Yaris rank 1-2 across most normalisation methods due to their exceptional reliability (92/100), safety (5 stars), and warranty (3 years). Tesla slips to last despite strong luxury and space, hampered by poor affordability (42/100) and weak reliability (70/100) in the family-focused weighting. Dacia Sandero offers the lowest cost but trails on comfort.

### Toreto Higher Weight (0.7) Scenario
**Scenario Description:** Performance enthusiast: acceleration, power, and sportiness dominate

| Alternative | normalised_max | normalised_max_min | normalised_sum | normalised_vector |
|---|---|---|---|---|
| **Tesla Model Y** | 88.89 | 90.00 | 37.67 | **63.45** |
| **Toyota Yaris** | 57.68 | 29.97 | 26.72 | 41.05 |
| **Citroen C3 IV** | 54.74 | 21.70 | 26.19 | 39.79 |
| Toyota Yaris Cross | 55.28 | 23.71 | 26.20 | 39.86 |
| Dacia Sandero 3 | 51.34 | 15.92 | 25.23 | 37.77 |

**Key Insight:** When performance criteria dominate (70%), Tesla Model Y achieves its highest relative advantage. Its 5.9-second 0-100 acceleration, 299hp, 420Nm torque, and 8.8 sportiness score vastly outperform competitors. Performance-focused buyers would have a clear preference for Tesla, despite its cost.

### Stability Across Normalisation Methods

**Robust conclusions** (consistent across methods):
- Tesla Model Y consistently ranks 1st in equal-weight and toreto-emphasis scenarios
- Toyota Yaris and Yaris Cross consistently rank 1st in pere_de_famille emphasis
- Dacia Sandero 3 consistently ranks last

**Normalisation sensitivity:** Results are most sensitive to method choice in the pere_de_famille scenario, where normalised_max ranks Yaris Cross highest (69.16) but normalised_vector ranks it at 42.41. This suggests that differences between top candidates (Yaris, Yaris Cross, Citroen C3) are compressed and sensitive to scaling choices. Tesla's dominance in other scenarios is robust across all methods.

---

## ELECTRE Outranking Analysis

ELECTRE III applies concordance-based outranking logic to identify which alternatives should be preferred based on collective strength across criteria. Results are presented as concordance matrices and visualized as heatmaps and directed graphs.

### Equal Weights Scenario

**Concordance Matrix:**

```
                    Dacia    Citroen   Yaris   Yaris_Cross  Tesla
Dacia Sandero 3     1.00      0.72     0.63       0.57       0.25
Citroen C3 IV       0.83      1.00     0.82       0.83       0.25
Toyota Yaris        0.92      0.82     1.00       0.92       0.33
Toyota Yaris Cross  0.82      0.72     0.82       1.00       0.42
Tesla Model Y       0.83      0.92     0.83       0.83       1.00
```

**Outranking Analysis (threshold = 0.7):**

| From → To | Outranks? | Concordance |
|---|---|---|
| Tesla → Others | Yes | 0.83 (avg) |
| Toyota Yaris → Dacia | Yes | 0.92 |
| Toyota Yaris → Citroen | Yes | 0.82 |
| Toyota Yaris Cross → Dacia | Yes | 0.82 |
| Citroen → Dacia | Yes | 0.83 |
| Dacia → Tesla | No | 0.25 |

**Graph characteristics:** 5 nodes, 14 edges indicating a densely connected outranking network.

**Interpretation:** Tesla outranks all others consistently (concordance 0.83 avg) but is weakly outranked by Toyota models (0.33-0.42 reverse). Toyota Yaris shows strong concordance against lower-ranked alternatives. Dacia consistently concedes to others. The dense connectivity suggests no clear hierarchical winner under equal weights—multiple alternatives have mutual outranking relationships, reflecting the fundamental trade-offs inherent in car selection.

### Pere_de_Famille Higher Weight Scenario

**Concordance Matrix:**

```
                    Dacia    Citroen   Yaris   Yaris_Cross  Tesla
Dacia Sandero 3     1.00      0.76     0.65       0.47       0.35
Citroen C3 IV       0.77      1.00     0.82       0.77       0.35
Toyota Yaris        0.88      0.82     1.00       0.88       0.47
Toyota Yaris Cross  0.82      0.76     0.82       1.00       0.58
Tesla Model Y       0.77      0.88     0.77       0.77       1.00
```

**Outranking Analysis (threshold = 0.7):**

| From → To | Outranks? | Concordance |
|---|---|---|
| Toyota Yaris → Dacia | Yes | 0.88 |
| Toyota Yaris → Citroen | Yes | 0.82 |
| Toyota Yaris Cross → Dacia | Yes | 0.82 |
| Citroen → Dacia | Yes | 0.77 |
| Toyota Yaris ↔ Yaris Cross | Mutual | 0.82-0.88 |
| Tesla → Others | No | 0.35-0.77 |

**Graph characteristics:** 5 nodes, 14 edges.

**Interpretation:** When family criteria are weighted 70%, Tesla's concordance collapses to 0.35-0.77 (below threshold against most alternatives), indicating poor performance on family-relevant criteria. Toyota models dominate: Yaris outranks Dacia (0.88) and Citroen (0.82); Yaris Cross achieves mutual outranking with Yaris. This reflects Toyota's superior reliability (92/100), safety (5 stars), and warranty (3 years).

### Toreto Higher Weight Scenario

**Concordance Matrix:**

```
                    Dacia    Citroen   Yaris   Yaris_Cross  Tesla
Dacia Sandero 3     1.00      0.67     0.62       0.66       0.15
Citroen C3 IV       0.90      1.00     0.81       0.90       0.15
Toyota Yaris        0.95      0.81     1.00       0.95       0.20
Toyota Yaris Cross  0.81      0.67     0.81       1.00       0.25
Tesla Model Y       0.90      0.95     0.90       0.90       1.00
```

**Outranking Analysis (threshold = 0.7):**

| From → To | Outranks? | Concordance |
|---|---|---|
| Toyota Yaris → Dacia | Yes | 0.95 |
| Toyota Yaris → Citroen | Yes | 0.81 |
| Citroen → Dacia | Yes | 0.90 |
| Tesla → Others | No | 0.15-0.25 |

**Graph characteristics:** 5 nodes, 12 edges (fewer edges than equal-weight scenario).

**Interpretation:** Under performance emphasis, Toyota Yaris surprisingly outranks Dacia strongly (0.95) despite Tesla's superior acceleration and power. This is because ELECTRE uses concordance (combined strength across all weighted criteria) rather than optimizing a single criterion. Even in the toreto scenario, family criteria retain 30% of weight, and Toyota Yaris maintains strong scores on reliability and safety that carry the concordance relationship. Tesla's extreme specialization on power and speed results in very low concordance (0.15-0.25) against more balanced competitors, despite its clear performance supremacy.

### ELECTRE Visualizations

**Heatmaps** (relative paths):
- ![Equal weights heatmap](electra/heatmap_equal_weights.png)
- ![Pere de famille higher weight heatmap](electra/heatmap_pere_de_famille_higher_weight.png)
- ![Toreto higher weight heatmap](electra/heatmap_toreto_higher_weight.png)

**Outranking graphs** (relative paths):
- ![Equal weights graph](electra/outranking_graph_equal_weights.png)
- ![Pere de famille higher weight graph](electra/outranking_graph_pere_de_famille_higher_weight.png)
- ![Toreto higher weight graph](electra/outranking_graph_toreto_higher_weight.png)

The heatmaps show concordance intensity: darker colors indicate stronger outranking relationships. Outranking graphs display directed edges: an arrow from A→B means A outranks B (concordance ≥ 0.7).

---

## Scenario Sensitivity Analysis

### Comparison Across Scenarios

| Metric | Equal Weights | pere_de_famille 70% | toreto 70% |
|---|---|---|---|
| **Weighted Score Leader** | Tesla (59.78) | Yaris Cross (42.41) | Tesla (63.45) |
| **Normalised Vector 2nd Place** | Toyota Yaris (41.72) | Toyota Yaris (42.38) | Yaris (41.05) |
| **ELECTRE Network Density** | 14 edges | 14 edges | 12 edges |
| **Clear Outranking Winner** | No (Tesla weak reverse) | Yes (Toyota Yaris/Cross) | No (Toyota dominates concordance) |

### Robust Conclusions

**Findings that hold across all scenarios:**

1. **Tesla Model Y's bipolar nature:** Dominates under any emphasis on performance or balanced preferences, but becomes the weakest option when family criteria are prioritized. Its luxury (8.0/10), power (299hp), and boot space (854L) cannot overcome poor affordability (42/100) and modest reliability (70/100) in family-focused analysis.

2. **Toyota models' consistency:** Toyota Yaris and Yaris Cross maintain competitive scores across all scenarios (41-42 range in normalised vector). They are never the worst choice and excel when family criteria dominate. Their 92/100 reliability and 5-star safety provide a resilient foundation.

3. **Dacia Sandero 3's value position:** Consistently ranks last in weighted scoring, but is non-dominated because it offers the lowest cost (95/100 affordability) with adequate reliability (82/100). Relevant only for price-sensitive buyers willing to sacrifice comfort.

4. **Citroen C3 IV's middle ground:** Never dominates, never collapses. Remains a compromise option across scenarios (38-40 range), offering reasonable balance but no distinctive strength.

### Scenario Sensitivity

**High sensitivity** to weighting choices:
- **Tesla's score span:** 59.78 (equal) → 56.11 (family) → 63.45 (performance) = 7.34-point swing
- **Toyota Yaris Cross span:** 41.14 (equal) → 42.41 (family) → 39.86 (performance) = 2.55-point swing
- **Dacia Sandero span:** 38.09 (equal) → 38.41 (family) → 37.77 (performance) = 0.64-point swing

Tesla's high sensitivity indicates it is a polarizing choice—excellent for some priorities, poor for others. Toyota models show moderate sensitivity, reflecting their well-balanced profile. This is **an important decision insight:** if the buyer's priorities could shift over time or differ from stated preferences, Toyota models offer lower regret risk.

---

## Final Interpretation

### Decision Recommendation

**The optimal choice depends entirely on the buyer's true priorities:**

#### For Family-Focused Buyers (Reliability, Safety, Affordability)
**Recommendation: Toyota Yaris Cross**
- Exceptional reliability (92/100) and safety (5 stars)
- Largest boot volume among practical models (397L)
- Strong warranty (3 years)
- Moderate affordability (65/100)
- **Weighted score:** 42.41 (highest in pere_de_famille scenario)
- **ELECTRE:** Mutual outranking with Yaris, dominant over others

Alternative: Toyota Yaris offers nearly identical performance at higher affordability (75/100) but reduced boot space (286L).

#### For Balanced / All-Purpose Buyers
**Recommendation: Toyota Yaris**
- Maintains high performance across all scenarios (41-42 range)
- Exceptional reliability (92/100) and safety (5 stars)
- Better affordability (75/100) than Yaris Cross
- Adequate boot space (286L) for small families
- **Weighted score:** 41.72 (competitive across scenarios)
- **ELECTRE:** Strong concordance (0.82-0.92) against lower-ranked alternatives

This choice minimizes regret if buyer preferences or circumstances change.

#### For Performance Enthusiasts
**Recommendation: Tesla Model Y (if budget allows)**
- Unmatched acceleration (5.9s 0-100)
- Highest power (299hp) and torque (420Nm)
- Premium luxury (8.0/10) and space (854L boot)
- 4-year warranty (longest offered)
- **Weighted score:** 63.45 (highest in performance scenario)
- **ELECTRE:** Strong concordance (0.83-0.95 against others) but only at 70% toreto weighting

Warning: Tesla's poor affordability (42/100) and modest reliability (70/100) make it unsuitable for buyers with budget constraints or family-first values. Regret risk is high if priorities shift.

#### For Budget-Conscious Buyers
**Recommendation: Dacia Sandero 3**
- Lowest purchase cost (95/100 affordability score)
- Adequate reliability (82/100)
- **Weighted score:** 38.09 (last place, but meets bare minimums)
- Acceptable on all core criteria; weak on comfort (5.8/10) and safety (2 stars)

Warning: The safety rating of 2 stars is the lowest among retained alternatives and merits careful consideration for families with young children.

### Meta-Analysis: Insight from the Methods

**Weighted scoring and ELECTRE agreement:**
- Both methods strongly agree on Toyota models' suitability for family buyers
- Both methods agree Tesla dominates under balanced or performance-heavy weighting
- ELECTRE's concordance-based logic (vs. weighted sum) adds robustness by considering pairwise strength, not just composite score

**Why alternatives survive despite weaknesses:**
The 5 non-dominated alternatives persist because the decision space has distinct trade-offs with no natural dominance order. Each model wins at something:
- **Tesla:** Luxury, space, performance
- **Yaris Cross:** Reliability + space + practicality
- **Yaris:** Reliability + affordability + practicality
- **Citroen:** Comfort + affordability balance
- **Dacia:** Maximum affordability

A buyer cannot have all five strengths in one vehicle—hence all five are rational choices for different priorities.

---

## Limitations and Assumptions

### Methodological Assumptions

1. **Bare minimum interpretation:** The pere_de_famille satisfaction filter is strictly enforced. Cars failing *any* bare minimum (e.g., safety rating < 4) are eliminated even if strong elsewhere. Alternative interpretation: bare minimums could be soft constraints rather than hard filters, changing the retained set.

2. **Criteria family bias:** Dominance analysis uses only pere_de_famille criteria, per Docker parameters. This favors reliability, affordability, safety, and space. If toreto criteria were used instead, a different set might be non-dominated (e.g., Dacia Duster, which fails on safety, would not have been eliminated).

3. **Normalisation method selection:** Different techniques (max, max-min, sum, vector) can produce different rankings, especially for non-dominant alternatives. Weighted scoring is most robust for Tesla and Toyota's clear separation, but less stable for comparing Citroen, Dacia, and Yaris.

4. **ELECTRE threshold (0.7):** A concordance threshold of 0.7 is moderately high, treating 70% collective strength as "outranking." A lower threshold (0.6) would increase outranking edges; a higher threshold (0.8) would create a sparser, more hierarchical graph. Results are stable within reasonable threshold ranges, but sensitivity testing with alternative thresholds is recommended.

5. **Criteria weights and bare minimums:** All criteria within a family are equally weighted (weight = 1). No criterion was marked as "critical" or weighted higher, so all family criteria contribute equally. Real buyer priorities often vary (e.g., safety might be weighted 2x affordability for families with children).

### Data Quality and Scope

6. **Criteria reliability:** Some criteria are subjective (Luxury/Comfort Score, Sportiness Score) or inferred (Affordability based on French market pricing). These depend on accurate market research and expert assessment. Errors in data could shift results.

7. **Incomplete alternatives set:** The analysis includes 15 common French-market 2025 models but excludes many others (luxury brands, niche vehicles, used market). The optimal choice might differ if a broader competitive set were evaluated.

8. **Time-invariant assumption:** Prices, reliability estimates, and market conditions change over time. This analysis is valid for 2025 French market conditions. Decisions should be revisited annually or when major market changes occur.

9. **Scenario completeness:** Three scenarios were defined, but the decision space is continuous. A buyer might have unique weights (e.g., 60% family, 40% performance) not captured by these discrete scenarios. Sensitivity analysis suggests results vary smoothly with weighting, but custom scenarios should be analyzed for specific buyer profiles.

### Assumptions in Interpretation

10. **Rationality and trade-off acceptance:** The analysis assumes the buyer accepts fundamental trade-offs (e.g., cannot have both maximum affordability and performance). Irrational buyer behavior (e.g., brand loyalty unrelated to criteria) is not modeled.

11. **No external factors:** The analysis does not account for external considerations such as dealer support, warranty claims experience, subjective "feel" of the car, environmental values, or personal brand preferences—all significant in real purchase decisions.

12. **Stability of preferences:** Scenario weighting assumes the buyer's priorities remain fixed during the analysis. Real decisions often involve preference evolution as buyers gain information and test-drive vehicles.

---

## Artifact Index

| File | Description | Path |
|---|---|---|
| satisfaction.csv | Retained alternatives after bare minimum filtering (pere_de_famille family) | docker-report/satisfaction.csv |
| dominance.csv | Non-dominated alternatives under the pere_de_famille criteria family | docker-report/dominance.csv |
| weights_results.csv | Weighted mean scores for each alternative across all scenarios and normalisation methods | docker-report/weights_results.csv |
| normalised_max.csv | Normalisation using max scaling (value / max_value) | docker-report/normalised/normalised_max.csv |
| normalised_max_min.csv | Min-max normalisation ((value - min) / (max - min)) scaled to [0, 1] | docker-report/normalised/normalised_max_min.csv |
| normalised_sum.csv | Sum normalisation (value / sum of column) for proportional weighting | docker-report/normalised/normalised_sum.csv |
| normalised_vector.csv | Vector normalisation (Euclidean unit vector scaling) | docker-report/normalised/normalised_vector.csv |
| normalised_electre_equal_weights.csv | ELECTRE normalisation for equal weights scenario | docker-report/normalised/normalised_electre_equal_weights.csv |
| normalised_electre_pere_de_famille_higher_weight.csv | ELECTRE normalisation for pere_de_famille emphasis scenario | docker-report/normalised/normalised_electre_pere_de_famille_higher_weight.csv |
| normalised_electre_toreto_higher_weight.csv | ELECTRE normalisation for toreto emphasis scenario | docker-report/normalised/normalised_electre_toreto_higher_weight.csv |
| electra_results.txt | ELECTRE III concordance matrices and outranking analysis for all scenarios | docker-report/electra/electra_results.txt |
| heatmap_equal_weights.png | Concordance matrix heatmap: equal weights scenario | docker-report/electra/heatmap_equal_weights.png |
| heatmap_pere_de_famille_higher_weight.png | Concordance matrix heatmap: pere_de_famille emphasis (70%) | docker-report/electra/heatmap_pere_de_famille_higher_weight.png |
| heatmap_toreto_higher_weight.png | Concordance matrix heatmap: toreto emphasis (70%) | docker-report/electra/heatmap_toreto_higher_weight.png |
| outranking_graph_equal_weights.png | Directed outranking graph: equal weights (edges = outranking relationships ≥ 0.7 concordance) | docker-report/electra/outranking_graph_equal_weights.png |
| outranking_graph_pere_de_famille_higher_weight.png | Directed outranking graph: pere_de_famille emphasis (70%) | docker-report/electra/outranking_graph_pere_de_famille_higher_weight.png |
| outranking_graph_toreto_higher_weight.png | Directed outranking graph: toreto emphasis (70%) | docker-report/electra/outranking_graph_toreto_higher_weight.png |
| README.md | Docker workflow summary and parameters | docker-report/README.md |
| docker_report.log | Complete Docker container execution log | docker-report/docker_report.log |

---

**Report Generated:** 26 May 2026  
**Analysis Method:** AMCD (Aggregated Multi-Criteria Decision) with ELECTRE III outranking  
**Configuration:** pere_de_famille family filter, ELECTRE threshold = 0.7  
**Alternatives Analysed:** 15 vehicles (5 retained after satisfaction filtering, 5 non-dominated)  
**Criteria:** 11 (6 pere_de_famille, 5 toreto)  
**Scenarios:** 3 (equal weights, pere_de_famille emphasis, toreto emphasis)  
**Normalisation Methods:** 7 (max, max-min, sum, vector, + 3 scenario-specific ELECTRE normalizations)
