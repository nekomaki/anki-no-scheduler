# Review Order by Knowledge Gain

Reorder your Anki queue by **expected knowledge gain** to maximize learning efficiency.

## How it works

This addon introduces a new review strategy that goes beyond Anki’s built-in options (like "easy cards first" or "descending retrievability"). It prioritizes cards that contribute the most to your long-term memory.

Long-term knowledge is estimated using an exponential moving average (EMA) of retrievability. This produces a score between 0 and 1 that reflects how well a card is expected to be remembered over time.

The addon calculates the expected gain in long-term knowledge for each card and reorders your review queue so that the cards with the highest expected gain are reviewed first.

## Features

- Reorders **learning** and **review** cards within the daily queue.
- Displays **expected knowledge gain** for each card.
- Compatible with FSRS 4.5, 5 and 6.

## Limitations

- **Undo is not supported.**
- This addon currently maximizes expected knowledge gain per single review. However, long-term knowledge is built over multiple reviews. New cards often yield low immediate gain, but their contribution increases significantly after a few successful reviews. For best results, use this addon alongside a well-tuned scheduler (e.g. with an appropriate desired retention setting).

## Installation

1. Install the addon from [AnkiWeb](https://ankiweb.net/shared/info/215758055).
2. Open Anki and go to **Tools > Add-ons**.
3. Click on **Get Add-ons** and enter the code `215758055`.
4. Restart Anki to activate the addon.

---

## Long-term knowledge computation

This addon estimates **long-term knowledge** using **exponential moving average (EMA)** retrievability:

$$
J_{\text{EMA}}(\text{card}, T; \gamma) = -\log \gamma \int_{0}^{\infty} R(\text{card}, T + t) \gamma^t \mathrm{d}t
$$

where

- $T$: time since the last review
- $R(\text{card}, T)$: retrievability of the card
- $\gamma$: exponential decay factor, typically around 0.99

For FSRS 4.5 and 5, there’s a closed-form expression for it:

$$
J_{\text{EMA}}(\text{card}, T; \gamma) = \sqrt{\pi\alpha\log\gamma} \cdot \text{erfcx}\left(\sqrt{(\alpha-T)\log\gamma}\right)
$$

where

- $\alpha = -\frac{\text{stability}}{\text{FACTOR}}$

For FSRS 6, the EMA knowledge is given by:

$$
J_{\text{EMA}}(\text{card}, T; \gamma) = \gamma^{\alpha-T} (\alpha\log\gamma)^{-D} \cdot \Gamma(D+1, (\alpha - T)\log\gamma)
$$

where

- $D$ and $F$: decay and factor of the card
- $\alpha = -\frac{\text{stability}}{\text{F}}$
- $\Gamma$: upper incomplete gamma function
