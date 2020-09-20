# FLASK REQUEST PRE PROCESSOR

Library to preprocess Flask app request generically with vanilla flask or with any other flask packages eg:flask_restful

Removes the need boilerplate code for extracting and type validating and type cast of request payload from rest api endpoint so that the endpoint can purely focus on the core logic implementation

All the extracted, validated, type casted, and/or aliased parameters will be passed to the endpoint as keyword arguments 


## Installation

    pip install Flask-RequestPreProcessor

### Dependencies
    
    python>=3.6
    Flask>=1.1.*
    funcargpreprocessor==0.1.*
    
## Usage

### Simple GET request

```python
from flask_requestpreprocessor import parse_request_query_param, DateArg

@parse_request_query_param(
    {
        'pageNo':{'data_type':int, 'alias':'page_no', 'min_val':1 }
        ,'count':{'data_type':int, 'value_list':[10,20,30,50,100] }
        , 'signedUpDate':{'data_type':DateArg('%Y-%m-%d'), 'alias':'signed_up_date'}
        , 'filterCondition2':{....}
        .....
    }
)
def get_user_list(page_no=1, count=10, signed_up_date=None, **other_filter_conditions):
    pass
```

## Parser definition
    