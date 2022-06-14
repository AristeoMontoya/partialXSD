# Partial XSD validator
Yet another _quick_ and dirty python script. A simple python script to validate a fragment of an xml to a schema.

## Instalation
`pip install -r requirements.txt`

## Usage
Help page:
 ```
positional arguments:
  target                File or dir to validate
  schema                XSD or directory containing XSD files to apply

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Log output
  -r, --recursive       Search recursively
```

Example:
```sh
# This will compare every xml in docs against every schema in docs/schemas including subdirectories and save the output to log.txt
python validator.py docs docs/schemas -r -o log.txt
```
