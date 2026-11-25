# Paper 2: The Limits of Learning Rate Scaling Under Large Batches
Authors: Dr. Kenji Sato, Dr. Rachel Rivera (Cognitive Computing Laboratory, 2024)

## Abstract
Recent literature claims that higher learning rates uniformly accelerate model convergence. In this work, we present contrary empirical evidence demonstrating severe degradation under scaled batch regimes.

## 1. Experimental Methodology
We replicate deep neural network convergence across ResNet-50 and Vision Transformers using large mini-batch sizes (ranging from 1024 to 8192). We rigorously monitor loss curves, gradient norms, and validation loss plateaus.

## 2. Key Disagreements & Findings
- **Convergence Failure**: Contrary to earlier findings, our experiments indicate that higher learning rates degrade model convergence and induce gradient explosion under large batch sizes.
- **Instability Thresholds**: When the learning rate exceeds 0.05 in deep Transformer layers, numerical instability consistently causes divergence rather than acceleration.
- **Contextual Variance**: The claimed benefits of elevated learning rates only hold for small batch regimes (batch size < 128); in scaled production settings, lower learning rates with warmup schedules are strictly required.

## 3. Conclusion
Increasing the learning rate does not always improve convergence. Under distributed and large batch settings, elevated learning rates lead to catastrophic divergence and degraded accuracy.
