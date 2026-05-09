## Failure Simulation Framework for Predictive Digital Twins

A stochastic damage evolution framework for predictive maintenance, validated against the IEEE PHM 2012 PRONOSTIA bearing run-to-failure dataset. The model uses a power-law damage equation with log-normal population variability across components:

$$\dot{D} = K_i \cdot L^a \cdot S^c \cdot D^\beta$$

where $K_i \sim \text{LogNormal}(\ln k, \sigma)$ represents the component-specific rate constant drawn from a population distribution. Fitted parameters ($\beta = 2.0$, $a = 0.96$, $c = 1.03$) are consistent with published bearing fatigue literature (Paris-law family). Monte Carlo simulation produces 95% confidence intervals on failure cycle that empirically cover **78.6% of unseen test bearings (11/14)** on the IEEE PHM 2012 dataset.

## Validation results

Validated against the IEEE PHM 2012 PRONOSTIA dataset: 17 bearings across 3 operating conditions. 5 bearings used for parameter fitting, 14 unseen bearings used for coverage testing. 3 bearings excluded with documented reasons (premature step-failure, atypical early-life spike, truncated record).

| Condition | Predicted 95% CI (cycles) | Bearings within CI |
|-----------|---------------------------|--------------------|
| 1 (1800 rpm, 4000 N) | [637, 4189] | 7 / 7 |
| 2 (1650 rpm, 4200 N) | [687, 4715] | 3 / 5 |
| 3 (1500 rpm, 5000 N) | [609, 4523] | 1 / 2 |
| **Overall** | | **11 / 14 = 78.6%** |

All three miscoverage events occurred in the lower tail (premature failures), consistent with manufacturing-defect failure modes outside the model's wear-degradation scope.

## Repository structure

```
.
├── damage_evolution_model.py          
├── rms_health_indicator.py           
├── validation_pronostia/              
│   ├── validate_pronostia.py          
│   ├── monte_carlo_validation.png    
│   ├── fit_vs_measured_training.png   
│   ├── normalized_damage_trajectories.png
│   └── all_bearings_trajectories.png
├── archive/                           
│   └── damage_evolution_model_v1.py   
├── VALIDATION.md                     
└── data/                             
```

## Reproducing the validation

The PRONOSTIA dataset is not redistributed in this repository. To reproduce:

1. Download the IEEE PHM 2012 PRONOSTIA dataset from the FEMTO-ST institute (registration required).
2. Place the unpacked `Learning_set/` and `Test_set/` directories under `data/PRONOSTIA/`.
3. Install dependencies:
```
   pip install numpy pandas scipy matplotlib
```
4. Run:
```
   python validation_pronostia/validate_pronostia.py
```

End-to-end runtime is approximately 5-10 minutes on consumer hardware, dominated by the initial RMS computation across all 17 bearings.

## Mathematical model

The deterministic core models damage evolution as a power-law function of operating conditions and current damage state:

$$\dot{D} = k \cdot L^a \cdot S^c \cdot D^\beta$$

This is the same mathematical family as the Paris-Erdogan fatigue crack growth law, with $D$ playing the role of normalised crack size and $\beta$ the role of the Paris exponent.

The stochastic extension introduces population variability through a per-component random rate constant:

$$K_i \sim \text{LogNormal}(\ln k, \sigma)$$

This captures the empirical observation that nominally identical components under identical operating conditions exhibit lifespans varying by factors of 3 to 25 times, driven by manufacturing variability, material heterogeneity, and installation effects. Sampling $K_i$ once per component, rather than per timestep, produces realistic variance without the central-limit-theorem averaging that affects per-step noise formulations.

## Methodology evolution

The model structure was refined iteratively during validation:

- **v1, additive self-acceleration form** $\dot{D} = k \cdot L^a \cdot S^c \cdot (1 + \gamma D)$. Produced near-linear damage trajectories that did not match the observed plateau-then-acceleration behaviour of bearing degradation.

- **v2, power-law form** $\dot{D} = k \cdot L^a \cdot S^c \cdot D^\beta$. Captures the accelerating degradation correctly. Fitted $\beta = 2.0$ is consistent with the Forman-Mettas family.

- **v2 stochastic, per-step Gaussian noise.** Failed: per-step noise averages out by central limit theorem, producing collapsed distributions on long simulations.

- **v2 stochastic final, per-component log-normal $K_i$.** Each component draws its rate constant once, then evolves deterministically. Captures population variance correctly. This is the form used in the validated framework.

The validated form is in `damage_evolution_model.py`. The earlier v1 form is preserved in `archive/` for transparency but is not recommended for use.

## Limitations

- The validation is on 14 unseen bearings; coverage statistics on this sample size carry significant uncertainty.
- The 95% CIs are wide (factor of approximately 6.6 in Condition 1). Useful for maintenance planning but not a precision instrument.
- $\sigma$ is estimated from 5 fitting bearings as a point estimate. A more rigorous treatment would treat $\sigma$ as itself uncertain and propagate that uncertainty through the Monte Carlo.
- The framework assumes a single failure mode. Bearings actually fail in distinguishable modes (inner race, outer race, ball, cage). Lower-tail miscoverage in the validation is consistent with premature-failure modes outside the wear-degradation scope.
- Validated only on bearings; transferability to other components is plausible from the mathematical structure but unvalidated here.

## Status

Research-stage code shared for transparency about methodology and validation results. Not production-ready software.
