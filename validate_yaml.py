import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml", "-q"], check=True)

import yaml

files = {
    "qa-ci.yml":      ".github/workflows/qa-ci.yml",
    "qa-nightly.yml": ".github/workflows/qa-nightly.yml",
}

all_ok = True
for name, path in files.items():
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        triggers = list(data.get("on", {}).keys())
        jobs     = list(data.get("jobs", {}).keys())
        print(f"\n[OK]  {name}")
        print(f"      Triggers : {triggers}")
        print(f"      Jobs     : {jobs}")
        for job_name, job in data.get("jobs", {}).items():
            steps = job.get("steps", [])
            env_vars = list(job.get("env", {}).keys())
            print(f"      > job '{job_name}' — {len(steps)} steps, env vars: {len(env_vars)}")
    except yaml.YAMLError as e:
        print(f"\n[ERR] {name} — YAML parse error:\n  {e}")
        all_ok = False
    except FileNotFoundError:
        print(f"\n[ERR] {name} — file not found at: {path}")
        all_ok = False

print("\n" + ("All YAML files are VALID." if all_ok else "ERRORS found — fix before pushing."))
sys.exit(0 if all_ok else 1)