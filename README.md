# `poc-champ`

Web-scrapping CLI tool to retrieve links to Github repositories containing 
POC (Proof of Concept) to CVE's of interest.

### Logic flow:

1. Send request to `cve.mitre.org` to retrieve related CVE's by keyword provided by user.
2. Using parsed response, search for POC repositories for each CVE with `DDG` search engine.
3. Return scrapped results in JSON format. Example output is:

```json
[
    {
        "CVE-1": [
            "https://github.com/username/CVE-1-POC-repo-1",
            "https://github.com/username/CVE-1-POC-repo-2",
            "https://github.com/username/CVE-1-POC-repo-3"
        ]
    },
    {
        "CVE-3": [
            "https://github.com/username/CVE-3-POC-repo-1"
        ]
    }
]
```

## Usage:

### Locally:

**Install:**
```
pip install <poc_champ_version.whl>
# or using poetry in root project directory
poetry install
```

**Run**
```console
$ poc-champ [OPTIONS]
# or as module
$ python -m poc_champ [OPTIONS]
```

### With Docker:
```console
$ docker build -t poc-champ .
$ docker run [--rm] poc-champ [OPTIONS] > output.json
```

**Options**:

* `-k, --keyword TEXT`: Keywords to find related CVE's by.  **[REQUIRED]**
* `-r, --range TEXT`: Filter CVE by year published.
If left empty, return set default range of 5 last years.       
Allowed formats:
    * `<year>`: to set particular year.
    * `<min_year>-<max_year>`: set year frame.
* `-o, --output TEXT`: Pass filename to save results into.
* `--secret`: Trust me.
* `--help`: Show this message and exit.
