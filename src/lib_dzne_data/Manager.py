import lib_dzne_data.functions


class Manager:
    def __init__(self, data, *, allow_None=False):
        self._allow_None = allow_None
        self._data = dict()
        for key, value in data.items():
            if callable(value):
                self._data[key] = value
            else:
                self._data[key] = self._copy(value)
        self._locks = set()

    def __getitem__(self, key):
        if not lib_dzne_data.functions.strkeyallowed(key):
            raise TypeError(f"{key.__repr__()} is not an allowed key! ")
        if callable(self._data[key]):
            if key in self._locks:
                raise KeyError()
            self._locks.add(key)
            func = self._data[key]
            ans = func(self.getitem)
            self._data[key] = self._copy(ans)
            self._locks.discard(key)
        return self._copy(self._data[key])

    def _copy(self, data):
        return lib_dzne_data.functions.copy(
            data,
            allow_None=self._allow_None,
        )

    def getitem(self, mainkey, /, *auxkeys):
        obj = self[mainkey]
        for key in auxkeys:
            try:
                obj = obj[key]
            except IndexError:
                return None
            except KeyError:
                return None
            except TypeError:
                return None
        return self._copy(obj)

    def calc(self):
        for n, m in self.functions.items():
            self.getitem(n)

    @property
    def data(self):
        return self._copy(self._data)
    
    def to_Series(self):
        return lib_dzne_data.functions.to_Series(self._data)
