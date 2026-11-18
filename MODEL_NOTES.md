# Member 2 | Classifier implementation, training and Bayesian optimisation

Compare Gaussian densities with empirical feature bins and explain group-wise validation.

## GaussianNB baseline

Fits a Gaussian distribution to each feature within each class, with variance smoothing 0.05. It combines feature likelihoods using conditional independence. Correlated distance features can produce overconfident scores.

In this trained version the parameter was 0.05. On the ten student-test trips, mean Top-1 was 85.42%, Macro F1 was 0.6983 and binary candidate log loss was 0.2417. On the example GPS observation the highest-scoring candidate was arc 17630 with score 0.984.

## HistogramNB baseline

Learns feature distributions using 12 quantile bins and smoothed counts. It can model skewed distributions, although binning loses detail and the independence assumption remains.

In this trained version the parameter was 12. On the ten student-test trips, mean Top-1 was 86.89%, Macro F1 was 0.7241 and binary candidate log loss was 0.1699. On the example GPS observation the highest-scoring candidate was arc 17630 with score 0.962.

Top-1 compares the chosen road with a point label inferred from the supplied reference route. Six saved experimental configurations represent five distinct classifiers. The tuned and baseline CART fits belong to the same family.
