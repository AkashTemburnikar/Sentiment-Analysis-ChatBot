# AI-Adaptive UI Demo (Contextual Bandit)

Zero-build static HTML/JS demo showing an **AI-based adaptive UI** using a **contextual multi-armed bandit** (epsilon-greedy).

- **Adaptation**: layout density (`dense`/`spacious`), card size (`small`/`large`), theme (`dark`/`light`).
- **Context**: time of day (morning/day/evening), viewport width (narrow/medium/wide), OS theme preference.
- **Rewards**: open (+1), favorite (+2), dismiss (−1), dwell bonus (≤ +1/30s).
- **Persistence**: per-context Q-values stored in `localStorage`.

## Run
Open `index.html` in a modern browser.

## References (include in your APA paper if cited)
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
- Li, L., Chu, W., Langford, J., & Schapire, R. (2010). A contextual-bandit approach to personalized news article recommendation. *WWW '10*. https://doi.org/10.1145/1772690.1772758

## Disclosure
Portions of this project were assisted by ChatGPT (GPT-5 Thinking). Author reviewed and modified the code.