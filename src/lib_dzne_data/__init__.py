import string as _str

import lib_dzne_filedata as _fd


class Manager:
    def __add__(self, other):
        return self._add(self, other)
    def __radd__(self, other):
        return self._add(other, self)
    def __init__(self, data):
        if issubclass(type(data), type(self)):
            data = data._data
        self._data = dict()
        for key, value in data.items():
            self.check_key(key)
            self._data[key] = self._clone_data(value)
        self._locks = set()
    def __getitem__(self, key):
        if type(key) is tuple:
            keys = key
        else:
            keys = (key,)
        ans = self._getitem(*keys)
        return ans

    @classmethod
    def _clone_data(cls, data):
        if callable(data):
            return data
        else:
            return cls._clone_toml_data(data)
    @classmethod
    def _clone_toml_data(cls, data):
        ans = _fd.TOMLData.clone_data(data, toplevel=False)
        cls.check_toml_keys(ans)
        return ans
    @classmethod
    def _add(cls, *objs):
        ans = dict()
        for obj in objs:
            data = cls(obj)._data
            ans = dict(**ans, **data)
        ans = cls(ans)
        return ans
    @classmethod
    def legal_key_chars(cls):
        return _str.ascii_lowercase + _str.digits + '_'
    @classmethod
    def check_toml_keys(cls, data):
        objs = [data]
        while len(objs):
            obj = objs.pop(-1)
            if type(obj) in (str, int, bool, float):
                pass
            elif type(obj) is list:
                objs += obj
            elif type(obj) is dict:
                for k, v in obj.items():
                    cls.check_key(k)
                    objs.append(v)
            else:
                raise TypeError

    @classmethod
    def check_key(cls, value, toplevel=True):
        if (not toplevel) and (type(value) is int):
                return
        if type(value) is not str:
            raise TypeError(f"{value.__repr__()} is not a valid key as it is of the type {type(value).__name__} and not of the type str! ")
        if value == "":
            raise ValueError("'' is not a valid key! ")
        illegal = set(value) - set(cls.legal_key_chars())
        illegal = list(illegal)
        illegal.sort()
        illegal = [x.__repr__() for x in illegal]
        illegal = ", ".join(illegal)
        if len(illegal):
            raise ValueError(f"The key {value.__repr__()} contains the illegal chars {illegal}! ")
    @classmethod
    def is_legal_key(cls, value, toplevel=True):
        try:
            cls.check_key(value, toplevel=True)
        except:
            return False
        else:
            return True
    @classmethod
    def _flatten(cls, key, value):
        if type(value) is dict:
            return cls._flatten_dict(key, value)
        if type(value) is list:
            return cls._flatten_list(key, value)
        if type(value) in (str, int, bool, float):
            return {key: value}
        raise TypeError()
    @classmethod
    def _flatten_dict(cls, oldkey, oldvalue):
        ans = dict()
        for k, v in oldvalue.items():
            flattened = cls._flatten((k,), v)
            for innerkey, innervalue in flattened.items():
                ans[oldkey + innerkey] = innervalue
        return ans
    @classmethod
    def _flatten_list(cls, oldkey, oldvalue):
        ans = dict()
        for i, x in enumerate(oldvalue):
            flattened = cls._flatten((i,), x)
            for innerkey, innervalue in flattened.items():
                ans[oldkey + innerkey] = innervalue
        return ans

    @property
    def data(self):
        return self.tomlData.data
    @property
    def tomlData(self):
        self.calc()
        return _fd.TOMLData(self._data)

    def _getitem(self, *keys):
        if len(keys) == 0:
            return self.data
        mainkey, *auxkeys = keys
        self.check_key(mainkey)
        if callable(self._data[mainkey]):
            self._data[mainkey] = self._callitem(mainkey)
        ans = self._data[mainkey]
        for auxkey in auxkeys:
            self.check_key(auxkey, toplevel=False)
            try:
                ans = ans[auxkey]
            except:
                raise KeyError
        ans = self._clone_toml_data(ans)
        return ans
    def _callitem(self, key):
        if key in self._locks:
            raise ValueError
        try:
            self._locks.add(key)
            ans = self._data[key](self.get)
        finally:
            self._locks.discard(key)
        return self._clone_toml_data(ans)
    def get(self, *keys, default=None):
        if len(keys) == 0:
            return self.data
        if keys[0] not in self._data.keys():
            raise KeyError
        try:
            return self[*keys]
        except KeyError:
            return default
    def keys(self):
        return list(self._data.keys())
    def calc(self):
        keys = self.keys()
        for k in keys:
            self._getitem(k)
    def flatten(self):
        flattened = self._flatten_dict(tuple(), self.data)
        ans = dict()
        for tuplekey, value in flattened.items():
            strkey = '.'.join(str(x) for x in tuplekey)
            ans[strkey] = value
        return ans
    @classmethod
    def _unflatten_value(cls, value):
        if type(value) is str:
            return str.__repr__()
        if type(value) is int:
            return str(value)
        if type(value) is float:
            return str(value)
        if type(value) is bool:
            return str(value).lower()
        raise TypeError
    @classmethod
    def unflatten(cls, row):
        row = dict(row)
        txtData = _fd.TXTData.load("")
        for rawkey, rawvalue in row.items():
            key = str(rawkey)
            for k in key.split('.'):
                cls.check_key(k, toplevel=False)
            value = cls._unflatten_value(rawvalue)
            txtData.append(key + " = " + value)
        text = str(txtData)
        tomlData = _fd.TOMLData.from_str(text)
        data = tomlData.data
        ans = cls(data)
        return ans




