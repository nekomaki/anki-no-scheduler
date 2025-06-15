# Review Order by Knowledge Gain

Reorder your Anki queue by **expected knowledge gain** to maximize learning efficiency.

Work in progress, but already functional.

## Features

- Reorders **new**, **learning**, and **review** cards within the daily queue
- Compatible with FSRS V5 and V6

## Limitations

- **Undo is not supported**
- Performance may degrade on large decks

---

## Knowledge computation

This addon estimates **long-term knowledge** using **exponential moving average (EMA)** retrievability:

$$
J_{\text{EMA}}(\text{card}, T; \gamma) = -\ln \gamma \int_{0}^{\infty} R(\text{card}, T) \gamma^t \mathrm{d}t
$$

where

* $T$: time since the last review
* $R(\text{card}, T)$: retrievability of the card
* $\gamma$: exponential decay factor, typically around 0.99

For FSRS 4.5 and 5, there’s a closed-form expression for it:

$$
J_{\text{EMA}}(\text{card}, T; \gamma) = \sqrt{\pi A} \, \text{erfcx}\left(\sqrt{A - T \ln \gamma}\right)
$$

where

* $S$: stability of the card
* $A = -\frac{S}{\text{FACTOR}} \ln \gamma$

For FSRS 6, the EMA knowledge is given by:

$$
J_{\text{EMA}}(\text{card}, T; \gamma) = \gamma^{-S/F-T} (cS / F)^{-D} \cdot \Gamma(D+1, c(T + S/F))
$$

where

* $D$ and $F$: decay and factor of the card
* $c = -\ln \gamma$
