# Public equipment evidence distillation — 2026-08-19

## Purpose

This evidence note records public facts used to challenge and improve generic
equipment-development Skills. Company and product names remain evidence-source
labels only; they are not routing keys, architecture defaults or implied
endorsements. No customer layouts, internal recipes, unpublished limits or
workplace-specific implementation details are included.

## Source policy

- Prefer manufacturer product pages and manufacturer-hosted documents.
- Separate direct public facts from engineering inferences.
- Generalize only mechanisms observed across more than one equipment example or
  independently justified by equipment semantics.
- Keep numerical claims out of Skill rules unless they define a generic test
  fixture; vendor-specific counts remain evidence examples.

## Leading Precision public evidence

Official sources:

- [Company overview](https://www.lpitw.com/newweb/TW/Default.aspx)
- [PVD multi-chamber production platform](https://www.lpitw.com/newweb/TW/Product01.aspx)
- [Super Mini Batch Degas public brief](https://lpitw.com/newweb/images/mbd2.pdf)
- [Customized equipment and systems](https://lpitw.com/newweb/TW/Product03.aspx)

Public facts used (`DIRECT` means stated by the linked manufacturer source):

- `DIRECT` — The PVD platform combines an EFEM, load locks, a vacuum transfer mainframe and
  configurable process modules including deposition, pre-clean and mini-batch
  degas.
- `DIRECT` — The public examples include single-wafer process chambers and a
  multi-wafer batch chamber. `INFERENCE` — A physical platform facet therefore
  cannot safely be modeled as one identical processing server by default.
- `DIRECT` — The public degas brief describes four wafer stages, individually controlled
  heating and shared chamber evacuation, illustrating capacity with both
  per-position and shared-resource semantics.
- `DIRECT` — The platform lists different substrates and process modules.
  `INFERENCE` — Simulator route feasibility should therefore be capability- and
  material-dependent rather than copied from one fixed chamber drawing.

Generalized engineering inferences (not vendor specifications):

- Cluster topology nodes now declare process cardinality and internal coupling.
- WPH simulation now distinguishes single-unit, mini-batch, coupled/twin-position
  and independently parallel resources.
- Recipe steps use capabilities such as degas, pre-clean, deposition and
  metrology; vendor chamber names and facet counts are not universal rules.

## Applied Materials public evidence

Official sources:

- [Semiconductor product portfolio](https://www.appliedmaterials.com/us/en/semiconductor/products.html)
- [Producer HARP and Twin Chamber architecture](https://www.appliedmaterials.com/us/en/product-library/producer-harp.html)
- [Kinex integrated die-to-wafer hybrid bonding](https://www.appliedmaterials.com/eu/en/product-library/kinex-integrated-die-to-wafer-hybrid-bonding-system.html)
- [Actionable Insight Accelerator](https://www.appliedmaterials.com/us/en/semiconductor/solutions-and-software/ai-x.html)

Public facts used (`DIRECT`) and engineering interpretation (`INFERENCE`):

- `DIRECT` — The Producer page names a Twin Chamber architecture and simultaneous
  multi-wafer processing. `INFERENCE` — A simulator must declare whether its
  positions share or independently own resources and synchronization; the page
  is not used to assume a specific hidden subsystem layout.
- `DIRECT` — The Kinex example integrates wet clean, plasma activation and in-situ overlay
  metrology, and identifies queue-time control, cleanliness, die-level
  traceability and multi-binning as production concerns.
- `DIRECT` — Applied's public software material distinguishes process/chamber observations,
  metrology, recipe optimization and digital-twin experiments. A model output is
  therefore not automatically equipment readback or calibrated evidence.

Generalized engineering inferences (not vendor specifications):

- Cluster recipes may carry queue-time, residency, preparation and metrology
  evidence requirements.
- Bonder/debonder guidance now distinguishes reversible temporary carrier
  bonding from permanent wafer-to-wafer and die-to-wafer hybrid bonding.
- Die-to-wafer simulations preserve die source/bin/site lineage and attach
  metrology evidence to exact assemblies.
- Simulation scenario fingerprints include topology, recipe, cardinality,
  scheduling, reliability and measurement contracts.

## Deliberate exclusions

- Vendor performance and market-leadership claims are not acceptance criteria.
- Product-specific chamber counts, rates, temperatures, pressures, materials,
  maintenance intervals and recipes are not copied into Skill defaults.
- Hybrid bonding is not used to infer temporary debond behavior.
- Digital-twin availability is not treated as proof of model calibration.

## Eval impact

Behavior cases require agents to reject facet-count arithmetic, distinguish
batch/coupled/independent resource semantics, preserve queue-time and metrology
evidence, and keep temporary versus hybrid bonding lifecycles separate. These
cases are vendor-neutral and may be released publicly after the full lifecycle
gates pass.
