---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst,ipynb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Roulette output regression test

```{code-cell} ipython3
import pandas as pd
df = pd.read_csv( "roulette.csv", index_col="filename" )
display( df.head() )
```

```{code-cell} ipython3
with open("baseline.config","r") as f:
    fn = f.read()
fn = fn.strip() + ".csv"
print( fn )
```

```{code-cell} ipython3
bl = pd.read_csv( fn, index_col="filename" )
display( bl.head() )
```

```{code-cell} ipython3
diff = df - bl
```

```{code-cell} ipython3
display( diff.mean() )
```

```{code-cell} ipython3
display( diff.abs().mean() )
```
