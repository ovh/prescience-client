# Problem types
What are the kinds of machine learning problem type you could encounter :

* Classification (prescience code : `classification`)
* Regression (prescience code : `regression`)
* Time-series Forecast (prescience code : `time_series_forecast`)
* Time-series Classification (not available in prescience yet)

## How to know which kind of problem are you facing ?

|                         	| You're trying to predict a continous value 	| You're trying to predict a category 	|
|-------------------------	|--------------------------------------------	|-------------------------------------	|
| Your data have NO order 	| Regression                                 	| Classification                      	|
| Your data are ordered   	| Time-series Forecast                       	| Time-series Classification          	|