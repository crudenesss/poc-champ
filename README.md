# `poc-champ`

Web-scrapping CLI tool to retrieve links to Github repositories containing 
POC (Proof of Concept) to CVE's of interest.

### Logic flow:

1. Send request to `cve.mitre.org` to retrieve related CVE's by keyword.
2. Using parsed response, search for POC repositories for each CVE with `DDG` search engine.
3. Return scrapped results in JSON format.

## Usage:

### How to run...

#### Locally:
```console
$ poc-champ [OPTIONS]
# or
$ python -m poc_champ [OPTIONS]
```

#### With Docker:
```console
$ docker build -t poc-champ .
$ docker run [--rm] -v <preferred_host_destination>:/poc-champ/output poc-champ [OPTIONS]
```

**Note:** You'll need `-v` option above especially if you plan on saving output to files on your host machine. 

**Options**:

* `-k, --keyword TEXT`: Keywords to find related CVE's by.  [required]
* `-r, --range TEXT`: Filter CVE by year published.
If left empty, return set default range of 5 last years.       
Allowed formats:
    * `<year>`: to set particular year.
    * `<min_year>-<max_year>`: set year frame.
* `-o, --output TEXT`: Pass filename to save results into.
* `--secret`: Trust me.
* `--help`: Show this message and exit.

---

### Parameters:
    keyword (Annotated[str, typer.Option]):
    Required option. Provide keywords to later find related CVE.

    year_range (Annotated[Optional[str], typer.Option], optional): 
    Provide year time frame. Defaults to None, which results in setting the timeframe of
    last 5 years.

### Raises:
    typer.Exit:
    If particular exceptions arise, exit POCChamp gracefully.
