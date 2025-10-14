# Expense Sharing App

## How to use

### Preparing the Environment

#### 1. clone the repo to your drive and open terminal into the xpns folder 
   
#### 2.1 install uv using terminal (linux):
   
```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2.2 install uv using terminal (windows):
   
```
winget install --id=astral-sh.uv  -e
```
restart terminal to load new environment variables.

for other windows installation methods refer to [uv docs](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).

#### 3. create the python virtual environment using:
```
$ uv sync
```

#### 4. activate virtual environment:

linux
```
$ source .venv/bin/activate
```
windows (cmd)
```
.venv\Scripts\activate.bat
``` 
>Notice: if you're using vscode, as soon as you sync the environment, it prompts you to use the env. you can use that instead of the command above.

windows (powershell)
```
.venv\Scripts\activate.ps1
```

### Runnning/Serving the app (dev)

#### 5. run the app:
```
flask run --host 0.0.0.0 --port 5000
```

#### 6. open the link shown in your terminal window.


#### 7. open an issue if there's any problem.

*I'd serve the app in production using nginx & gunicorn. though it's not yet fully production-ready, it's best to serve it in this manner.*

---

> This app is distributed under GNU General Public License v3.0. 
>
> there is a copy of the licensing terms included in LICENSE.md for convenience. 
