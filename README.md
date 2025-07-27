# No Scheduler – Review Order by Long-term Knowledge Gain

No scheduler. No leech concerns. No review history burden.

This addon reorders your Anki queue by **expected knowledge gain** to maximize learning efficiency.

## Usage

1. Enable FSRS and this addon in Anki.
2. Set the desired retention to 0.9 or higher in the deck's FSRS settings.
3. Set your preferred daily learning and review limits.
4. Start learning.
5. Increase learning/review limits in Custom Study if you want to learn more.

## How it works

This addon introduces a new review strategy that goes beyond Anki’s built-in options (like "easy cards first" or "descending retrievability"). It prioritizes cards that contribute the most to your long-term memory so that the cards with the highest expected gain are reviewed first.

The long-term knowledge is estimated using an exponential moving average (EMA) of retrievability. This produces a score between 0 and 1 that reflects how well a card is expected to be remembered over time.

## Features

- Reorders **learning** and **review** cards within the daily queue.
- Displays **expected knowledge gain** for each card.
- Estimates knowledge gain from future reviews.
- Compatible with FSRS 4.5, 5 and 6.

## Limitations

- **Undo is not supported.**
- FSRS 6 currently lacks a short-term memory model, and the knowledge gain of same-day reviews is a constant. This addon disables same-day reviews by default. Once FSRS supports short-term memory modeling, future updates will integrate it and add support for exam mode.

## Todos

- [ ] Add fuzzer.
- [ ] Add exam mode.

## Installation

Install from [AnkiWeb](https://ankiweb.net/shared/info/215758055).

1. Open Anki and go to **Tools > Add-ons**.
2. Click on **Get Add-ons** and enter the code `215758055`.
3. Restart Anki to activate the addon.

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
