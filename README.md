## NSAPH Utils python package

This package is intended to hold python code that will be useful
across multiple portions of the NSAPH pipelines.

There are open questions about how best to structure this that we can address
(i.e. do we do multiple modules within this module, 1 single module, etc).

## Current Development

- Interpolatation code: We have re-implemented the logic used for the 
  initial moving average interpolation used in the R based pipelines. 
  Developing better metholdologies remains to be done.
  
 ## TODO
 
 - Generic `Data` object that other NSAPH modules can inherit from.
 - Creation of list of other useful general features
 - Review of already done development to see what would make sense to port to this package