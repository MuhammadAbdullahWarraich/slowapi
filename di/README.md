# How to use in real FastAPI project?

Add this code to your main file:


```python
class SlowAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def get(self, *args, **kwargs): # add similar code for other types of requests
        dec = FastAPI.get(self, *args, **kwargs)
        def func(req_handler):
            req_handler = generic_di(req_handler)
            ret = dec(req_handler)
            return ret
        return func
app = SlowAPI()
```

After that, add routes as normal