from typing import Annotated
from slowapi import SlowAPI, Depends


app = SlowAPI()

def get_message_from_harry_bhai():
    print("assalamualaikum harry bhai!")
    yield "pehle aap bolo"
    print("arre harry bhai aap k aage koi bol skta h kya!")

@app.get('/')
def homepage(request, harrybhaikamessage: Annotated[str, Depends(get_message_from_harry_bhai)]):
    print(f"got this from harry bhai: {harrybhaikamessage}")
    # return JSONResponse({'hello': 'brother'})
    return {'hello': 'brother'}