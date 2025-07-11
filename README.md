# Expense Sharing App

## How to use

### Preparing the Environment

1. clone the repo to your drive and open terminal into the xpns folder 
   
2. install uv using terminal (linux):
   
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

for windows installation methods refer to [uv docs](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).

3. create a python virtual environment using:
```
uv sync
```

### Runnning/Serving the app (dev)

4. run the app:
```
flask run --host 0.0.0.0 --port 5000
```

5. open the link shown in your terminal window.


6. open an issue if there's any problem.

*I'd serve the app in production using nginx & gunicorn. though it's not yet fully production-ready, it's best to serve it in this manner.*

---

> This app is distributed under GNU General Public License v3.0. 
>
> there is a copy of the licensing terms included in LICENSE.md for convenience. 
