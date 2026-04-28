# (C) 2024,2026: Hans Georg Schaathun <georg@schaathun.net> 

class Parameters:
    """
    The Parameters class wraps the commandline arguments as well as a CSV 
    row as a dict-like object.

    The constructor can take either an `ArgumentParser` object (`args`) or
    a flat `dict` structure (`cfg`) as well as a nested `dict` (`hcfg`)
    as given by a TOML file.  Only selected parameters are used from the
    TOML format, and they will never override `args`/`cfg` parameters.

    For executable scripts, one can use `CosmoParser` object directly as
    the `args` argument, in addition to a TOML file if available.
    For API use, one should normally use the `cfg` argument.

    To add a row from the dataset, use the `serRow()` method.  Values
    from the row will always override other parameters.
    """
    def __init__(self,args=None,cfg=None,hcfg=None):
        if args:
            self._args = args.__dict__
            if cfg is not None:
                raise ValueError( "Cannot specify both args and cfg." )
        elif cfg:
            self._args = cfg
        else:
            self._args = {}
        self._row = {}
        if hcfg:
            cfg1 = hcfg["simulator"]
            if "cropsize" not in self._args:
                self._args["cropsize"] = cfg1.get( "cropsize", 256 )
            if "imagesize" not in self._args:
                self._args["imagesize"] = cfg1.get( "imagesize", 512 )
            if "source" not in self._args:
                try:
                    self._args["source"] = hcfg["source"]["mode"]
                except:
                    self._args["source"] = None
    def setRow(self,row):
        self._row = row
    def get(self,key,default=None,verbose=0):
        r = self._args.get( key, default )
        r = self._row.get(key,r)
        return r
    def __getitem__(self,key):
        return self.get(key)
    def __setitem__(self,key,v):
        self._row[key] = v

