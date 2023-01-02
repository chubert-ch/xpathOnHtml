# xpathOnHtml
Under construction: a python script to run xpath on html files (eventually)

Currently using inferred-namespace xpath (e.g. it'll try and infer that `//foo` should match `//bar:foo` if `bar` is the default namespace prefix) to query for every fragment matching that xpath in the given file/directory, with a bunch of options for output:

```
Find xml things specified by given xpaths

positional arguments:
  xpath                 xpath to search with, doesnt need standard corefiling
                        namespaces
  path                  path to search in, can be a file, directory or list of
                        files

optional arguments:
  -h, --help            show this help message and exit
  -p, --paths           output paths of found files
  -l, --linenumnode     output line number of node
  -F, --fullnode        output entire node
  -i, --inlinedfullnode
                        output entire node on one line
  -t, --toplinenode     output top line of node
  -c, --content         output content of node
  -n, --nonamespace     xpath wont attempt to infer namespaces
  -m NAMESPACEMAP, --namespacemap NAMESPACEMAP
                        namespace mapping in the form of
                        "prefix=http://example.com". Can repeat.
```
