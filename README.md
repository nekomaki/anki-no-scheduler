# No Scheduler – Review Order by Long-term Knowledge Gain

No scheduler. No leech concerns. No review history burden.

This addon reorders your Anki queue by **expected knowledge gain** to maximize learning efficiency.

## Usage

1. Enable FSRS and this addon in Anki.
2. Set the desired retention to 0.9 in the deck's FSRS settings.
3. Set your preferred daily learning and review limits.
4. Start learning.
5. Increase learning/review limits in Custom Study if you want to learn more.

## How it works

This addon introduces a new review strategy that goes beyond Anki’s built-in options (like "easy cards first" or "descending retrievability"). It prioritizes cards that contribute the most to your long-term memory so that the cards with the highest expected gain are reviewed first.

The long-term knowledge is estimated using discounted retrievability. This produces a score between 0 and 1 that reflects how well a card is expected to be remembered over time.

The future estimator uses a few steps of FSRS simulation to predict the knowledge gain from future reviews.

## Features

- Reorders **review** cards within the daily queue.
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

## Evaluation

The evaluation is based on [review-sort-order-comparison](https://github.com/open-spaced-repetition/review-sort-order-comparison), but using an unweighted setting where each review takes equal time. Future versions of this addon may incorporate actual review time.

By default, this addon uses the discounted knowledge (`knowledge_gain_discounted_desc`). In the experiments, the exam mode (`knowledge_gain_delayed_desc`) achieved the best performance.

| order                         | total_learned | total_time | total_remembered | average_true_retention | seconds_per_remembered_card |
|------------------------------|----------------|-------------|-------------------|-------------------------|------------------------------|
| knowledge_gain_delayed_desc  | 20000          | 96464.0     | 16192             | 0.751                   | 5.96                         |
| knowledge_gain_discounted_desc | 20000        | 96423.0     | 16030             | 0.728                   | 6.02                         |
| difficulty_asc               | 20000          | 96519.0     | 15737             | 0.793                   | 6.13                         |
| PSG_desc                     | 20000          | 96490.0     | 15701             | 0.784                   | 6.15                         |
| due_date_asc                 | 20000          | 96508.0     | 15619             | 0.678                   | 6.18                         |
| random                       | 20000          | 96483.0     | 15470             | 0.700                   | 6.24                         |
| retrievability_asc           | 20000          | 96512.0     | 15141             | 0.715                   | 6.37                         |
| stability_desc               | 20000          | 96487.0     | 15049             | 0.792                   | 6.41                         |
| retrievability_desc          | 20000          | 96473.0     | 14926             | 0.797                   | 6.46                         |
| add_order_desc               | 20000          | 96508.0     | 14902             | 0.793                   | 6.48                         |
| PRL_desc                     | 20000          | 96469.0     | 14383             | 0.793                   | 6.71                         |
| interval_asc                 | 20000          | 96470.0     | 14338             | 0.792                   | 6.73                         |
| stability_asc                | 20000          | 96424.0     | 14325             | 0.793                   | 6.73                         |
| add_order_asc                | 20000          | 96501.0     | 13611             | 0.773                   | 7.09                         |
| interval_desc                | 20000          | 96474.0     | 13549             | 0.778                   | 7.12                         |
| difficulty_desc              | 20000          | 96531.0     | 13172             | 0.789                   | 7.33                         |

---

## Long-term knowledge computation

This addon estimates **long-term knowledge** using **discounted** retrievability:

$$
J_{\text{dis}}(\text{card}, T; \gamma) = -\log \gamma \int_{0}^{\infty} R(\text{card}, T + t) \gamma^t \mathrm{d}t
$$

where

- $T$: time since the last review
- $R(\text{card}, T)$: retrievability of the card
- $\gamma$: exponential decay factor, typically around 0.99

For FSRS 4.5 and 5, there’s a closed-form expression for it:

$$
J(\text{card}, T; \gamma) = \sqrt{\pi\alpha\log\gamma} \cdot \text{erfcx}\left(\sqrt{(\alpha-T)\log\gamma}\right)
$$

where

- $\alpha = -\frac{\text{stability}}{\text{FACTOR}}$

For FSRS 6, the discounted knowledge is given by:

$$
J_{\text{dis}}(\text{card}, T; \gamma) = \gamma^{\alpha-T} (\alpha\log\gamma)^{-D} \cdot \Gamma(D+1, (\alpha - T)\log\gamma)
$$

where

- $D$ and $F$: decay and factor of the card
- $\alpha = -\frac{\text{stability}}{\text{F}}$
- $\Gamma$: upper incomplete gamma function
