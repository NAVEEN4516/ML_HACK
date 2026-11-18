# Methods and measured results

## Data and labels

The supplied files contain 80 training trips (208,417 GPS points) and 10 student-testing trips (19,160 points). File indices are local to each trip. Longitude/latitude are converted to local metres with an equirectangular approximation at the mean trip latitude. This approximation suits these local trajectories. GPS rows with nonfinite or impossible coordinates are removed. Timestamp discontinuities are recorded and restart sequence decoding.

Each road is a straight segment between its supplied endpoints. Candidate generation indexes sampled segment interiors in 80 m grid cells. It searches a 5 by 5 cell neighbourhood and keeps six closest segments. When there are too few segments it searches the full graph. This is a local candidate heuristic and does not guarantee the global six nearest segments in every boundary case.

The reference file is a sequence of arc IDs rather than point-level labels. A monotone dynamic programme aligns observations to reference occurrences by minimizing the sum of capped point-to-segment distances. It allows skipping reference occurrences and remaining at the same occurrence. Results are therefore agreement with inferred labels. At intersections and repeated roads the alignment can be ambiguous. Its distance objective can favour distance-based predictors. Independent point labels would improve evaluation.

## Features and experimentation

Seven features encode log distance, heading agreement, log road length, projection fraction, log speed, relative distance, and the product of distance and heading agreement. Features use GPS and the road graph only. The centered heading window uses two points on each side, so this system processes complete trips.

The seed is 95. Up to 300 observations per training trip are sampled uniformly without replacement. All six candidates per sampled observation are included. Standardization is fitted within each training fold. There are three trip-grouped folds. The saved folds.json contains exact trip IDs. All validation and student-test observations are evaluated. The final fit uses samples from all 80 training trips.

| Model | Initial parameter | Objective and limitations |
|---|---|---|
| Logistic | L2 penalty 0.01 | Newton optimization of binary cross entropy. Linear interactions limit fit |
| GaussianNB | Variance smoothing 0.05 | Gaussian likelihood with conditional independence. Correlated features violate the assumption |
| HistogramNB | 12 quantile bins | Smoothed categorical likelihood per feature. Bin resolution and independence limit fidelity |
| LDA | Covariance ridge 0.1 | Shared-covariance Gaussian discriminant. Assumes shared class covariance |
| CART | Maximum depth 5 | Greedy Gini reduction at feature quantiles, 20 samples per child. Higher depth increases overfitting risk |

All algorithms are implemented in models.py using NumPy. Models predict binary candidate correctness. A candidate with the highest probability is selected for each observation. There is no global arc-ID class vocabulary.

The best baseline family by group CV Macro F1 was CART. An RBF Gaussian-process surrogate and expected-improvement acquisition searched integer depths 2 through 12. Three initial exploration points were followed by five Bayesian proposals. Depth 9 won with CV Macro F1 0.7457, compared with 0.7203 for depth 5. Student-test Top-1 increased from 0.8681 to 0.8845. The final full-training-trip Macro F1 was 0.7480, compared with 0.7767 on student testing. This run gives no large training-validation gap, but the small number of trips and inferred labels limit generalisation claims.

## Metrics

Per-trip Macro F1 averages road-class F1 across the union of predicted and reference arcs. Reported overall scores average trips equally. Precision and recall follow the same convention. Top-1 compares the selected arc to the aligned reference arc. Candidate miss rate includes observations whose reference arc was absent from the generated set.

Log loss is binary candidate classification loss, averaged across all candidate rows. It is measured before decoding. Inference timing in comparison.csv covers model scoring only; decoder_by_trip.csv adds decoding. Service verification timings include raw-data loading and feature extraction.

Continuity is the proportion of consecutive predictions that stay on an arc or enter an arc starting at the previous arc's end node. Sequence F1 is twice the longest-common-subsequence length divided by the sum of the lengths of collapsed predicted and reference sequences.

## Sequence model

Each hidden state is a candidate road segment. Emission potentials are candidate odds. Transition potentials are exp(-cost), with cost 0 for the same arc, 0.65 for immediate adjacency, and 6 for other transitions. Log-space Viterbi maximises the resulting chain score. The decoder normalises each row of transition weights to give a conditional probability distribution. This HMM-inspired implementation does not estimate a generative observation density.

A gap above 10 seconds or nonincreasing timestamp starts a new chain. A finite jump penalty lets the decoder recover when candidates cannot be connected immediately. As a consequence disconnected jumps can remain. The output is one selected road segment per valid observation. No shortest-path interpolation is inserted between distant selected segments. These limitations must be explained during the demonstration. The costs were selected using mean ordered sequence F1 on out-of-fold training predictions. decoder_search.csv covers all six settings.

## Artifacts

CSV files record actual experiments. Six per-model JSON artifacts and the final model.json permit audit and deployment. The model.json also records feature order, decoder costs and seed. Charts are generated directly from the CSV files. Epoch loss curves do not apply to these implementations.

## Run provenance

The comparison, trial, decoder-search and per-trip tables in this checkout were generated in the same Windows reproduction. The original browser run and the reproduction are compared in the repository README. The reserved evaluation trips and the physical two-laptop demonstration remain pending.
