# Scoring Metrics

Here are the different scoring metrics available in prescience

## Scoring Metrics for classification

### ACCURACY

Prescience code : `accuracy`

Classification accuracy is the number of correct predictions made as a ratio of all predictions made.

This is the most common evaluation metric for classification problems, it is also the most misused. It is really only suitable when there are an equal number of observations in each class (which is rarely the case) and that all predictions and prediction errors are equally important, which is often not the case.

```
accuracy    = correct_predictions / total_elements
            = (True positives + True negatives) / total_elements
```

### PRECISION AND RECALL

Prescience codes : `precision` and `recall`

![precision_recall](https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Precisionrecall.svg/700px-Precisionrecall.svg.png)

![precision](https://miro.medium.com/max/888/1*C3ctNdO0mde9fa1PFsCVqA.png)

![precision_tab](https://miro.medium.com/max/1520/1*PULzWEven_XAZjiMNizDCg.png)

![recall](https://miro.medium.com/max/836/1*dXkDleGhA-jjZmZ1BlYKXg.png)

![recall_tab](https://miro.medium.com/max/1520/1*BBhWQC-m0CLN4sVJ0h5fJQ.jpeg)

### F1

Prescience code : `f1`

![F1](https://miro.medium.com/max/564/1*T6kVUKxG_Z4V5Fm1UXhEIw.png)

## ROC

Prescience code : `roc_auc`

Area under ROC Curve (or AUC for short) is a performance metric for binary classification problems.

The AUC represents a model’s ability to discriminate between positive and negative classes. An area of 1.0 represents a model that made all predictions perfectly. An area of 0.5 represents a model as good as random.

ROC can be broken down into sensitivity and specificity. A binary classification problem is really a trade-off between sensitivity and specificity.

* Sensitivity is the true positive rate also called the recall. It is the number instances from the positive (first) class that actually predicted correctly.
* Specificity is also called the true negative rate. Is the number of instances from the negative class (second) class that were actually predicted correctly.

You can learn more on wikipedia [here]https://en.wikipedia.org/wiki/Receiver_operating_characteristic)

## Scoring Metrics for regression

### MEAN SQUARED ERROR (MSE)

Prescience code : `mse`

The Mean Squared Error (or MSE) is much like the mean absolute error in that it provides a gross idea of the magnitude of error.

Taking the square root of the mean squared error converts the units back to the original units of the output variable and can be meaningful for description and presentation. This is called the Root Mean Squared Error (or RMSE).

![mse](https://wikimedia.org/api/rest_v1/media/math/render/svg/e258221518869aa1c6561bb75b99476c4734108e)

You can learn more on wikipedia [here](https://en.wikipedia.org/wiki/Mean_squared_error)

### MEAN ABSOLUTE ERROR (MAE)

Prescience code : `mae`

The Mean Absolute Error (or MAE) is the average of the absolute differences between predictions and actual values. It gives an idea of how wrong the predictions were.

The measure gives an idea of the magnitude of the error, but no idea of the direction (e.g. over or under predicting).

![mae](https://wikimedia.org/api/rest_v1/media/math/render/svg/3ef87b78a9af65e308cf4aa9acf6f203efbdeded)

You can learn more on wikipedia [here](https://en.wikipedia.org/wiki/Mean_absolute_error)

### R2

Prescience code : `r2`

The R2 (or R Squared) metric provides an indication of the goodness of fit of a set of predictions to the actual values. In statistical literature, this measure is called the coefficient of determination.

This is a value between 0 and 1 for no-fit and perfect fit respectively.

You can learn more on wikipedia [here](https://en.wikipedia.org/wiki/Coefficient_of_determination)