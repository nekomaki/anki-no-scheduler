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

# Knowledge Modeling in FSRS

## Snapshot vs. Story
Traditionally, FSRS defines the knowledge of a card as
$$J(\text{card},T)=R(\text{card}, T)$$
Here, $R(\text{card},T)$ is the retrievability of a card after $T$ days. This gives you a snapshot: one moment in time, one probability. Simple. But memory isn’t just about one day — it’s about the story that unfolds over many days.

## Modeling the Long-Term Knowledge
Let’s look at a few ways to move beyond a static measure, and start modeling long-term knowledge.

### 1. Delayed Retrievability: Fast Forward
The first idea is easy to grasp. Instead of asking “what’s your memory like now?” we ask “what will it be like *later*?”

Let $T$ be the time since the last review. Define a future offset $T_d$, and check retrievability not at $T$, but at $T + T_d$:

$$
J_{\text{delay}}(\text{card}, T; T_d) = R(\text{card}, T + T_d)
$$

It’s a simple change, but a useful one: it reflects your **long-range recall potential**. Instead of reacting to memory decay, we peek ahead and plan around it.

### 2. Average Retrievability: Area Under the Curve

Snapshots are fine. But often, we want to know **how well did I remember this card over time**, not just at the end.

Enter the **average retrievability**, defined as:

$$
J_{\text{AVG}}(\text{card}, T; T_d) = \frac{1}{T} \int_{0}^{T_d} R(\text{card}, T + t) \, dt
$$

This tells you: *over the past $T_d$ days, how accessible was this memory?* You get an intuitive number between 0 and 1, telling you how “alive” the memory was on average.


### 3. EMA Retrievability: Memory with a Decay Factor

Inspired by reinforcement learning and exponentially decaying rewards, we introduce **exponential moving average (EMA)** retrievability.

The idea: weigh recent retrievals more heavily than distant ones, but don’t discard the long-term. Use an exponential discount with decay factor $\gamma \in (0, 1)$:

$$
J_{\text{EMA}}(\text{card}, T; \gamma) = -\ln \gamma \int_{0}^{\infty} R(\text{card}, t) \gamma^t \, dt
$$

This integral gives you a weighted blend of present and future knowledge.

For FSRS-4.5 and FSRS-5, there’s a closed-form expression for it:

$$
J_{\text{EMA}}(\text{card}, T; \gamma) = \sqrt{\pi A} \, \text{erfcx}\left(\sqrt{A - T \ln \gamma}\right)
$$

where

* $T$ is the time since the last review
* $S$ is the stability of the card
* $A = -\frac{S}{\text{FACTOR}} \ln \gamma$


For FSRS-6, the EMA knowledge is given by:

$$
J_{\text{EMA}}(\text{card}, T; \gamma) = \gamma^{-S/F-T} (cS / F)^{-D} \cdot \Gamma(D+1, c(T + S/F))
$$

where

* $D$ and $F$ are the decay and factor of the card
* $c = -\ln \gamma$

## EMA for Learning Trajectories

One of the most powerful extensions is to apply EMA **across an entire learning history**, not just for a single memory instance.

If you define the retrievability as $R_f(\text{card}, T)$, then your long-term knowledge becomes:

$$
J_{\text{EMA}}(R_f(\text{card}, T); \gamma) = -\ln \gamma \int_{0}^{\infty} R_f(\text{card}, t) \gamma^t \, dt
$$
