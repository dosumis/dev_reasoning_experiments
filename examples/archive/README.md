# Archive — explorations that were superseded

Kept because the reasoning is recorded in the main
[examples/README.md](../README.md), and because the route is still viable if the requirements
change. Not part of the current proposal.

## 06-reified.ofn / 07-reified-class.ofn — reifying the temporal extent

Relate each continuant to its **temporal region** and do the Allen reasoning there.
`temporal region ⊑ occurrent` in BFO, so BFO's own `preceded_by` applies between regions with
no category error.

```
has_temporal_extent ∘ BFO:preceded_by ∘ extent_of  ⊑  starts_after_c
```

Works — 07 classifies at class level in OWL 2 EL, confirmed by ELK and HermiT.

**Superseded by [08-develops-from-timing.ofn](../08-develops-from-timing.ofn)**, which achieves
the same thing with no new primitive. Neither BFO nor RO supplies a
continuant→temporal-region relation (checked both: zero properties with a temporal-region
range), so this route requires inventing one. 08 does not.

Still worth having if Allen relations are ever wanted stated **directly between temporal
regions** rather than carried as superproperties of developmental relations.
