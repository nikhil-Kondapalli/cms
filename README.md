Here is a summary of the configuration and the different ways you can run all services:

---

### 1. Port Alignment (Completed)
The environment files have been aligned to ensure the gateway can route to upstream services:
* **API Gateway**: Port `8080` (routes to upstream services)
* **User Service**: Port `8001` in [user-service/.env](file:///Users/nikhilk/Workspace/cms-fastapi/user-service/.env)
* **Auth Service**: Port `8002` in [auth-service/.env](file:///Users/nikhilk/Workspace/cms-fastapi/auth-service/.env)
* **Content Service**: Port `8003` in [content-service/.env](file:///Users/nikhilk/Workspace/cms-fastapi/content-service/.env)

---

### 2. How to Run All Services

#### Method A: Process Manager (`Procfile.dev` + `honcho`)
We created [Procfile.dev](file:///Users/nikhilk/Workspace/cms-fastapi/Procfile.dev) at the root. Run with:
```bash
uvx honcho start -f Procfile.dev
```
* **Benefits**: Color-coded unified terminal output, isolated `uv` virtual environments, and clean shutdown on `Ctrl+C`.

---

#### Method B: VS Code / Antigravity IDE Debugger (One-Click F5)
We configured [.vscode/launch.json](file:///Users/nikhilk/Workspace/cms-fastapi/.vscode/launch.json) with a compound configuration:
1. Open the **Run & Debug** panel (`Ctrl+Shift+D` / `Cmd+Shift+D`).
2. Select **"Run All Services"** from the top dropdown.
3. Press **F5** (or click the green Play button).
* **Benefits**: Allows setting breakpoints, stepping through requests across services, and viewing dedicated terminal tabs for each service.

---

#### Method C: Lightweight Shell Script
We created and made executable [start-dev.sh](file:///Users/nikhilk/Workspace/cms-fastapi/start-dev.sh):
```bash
./start-dev.sh
```
* Runs all four services in the background and gracefully kills all processes when you press `Ctrl+C`.
