import collections
from copy import deepcopy

from winnow import utils

from winnow.values import value_factory, value_path_factory
from winnow.values.option_values import OptionResourceWinnowValue, OptionStringWinnowValue
from winnow.keys.key_matching import KeyMatcher
from winnow.exceptions import OptionsExceptionEmptyOptionValues, OptionsExceptionReferenceError

"""

OptionsSet

This is the beef.

all the logical operations on sieves actually happen in their options dict

"""

class OptionsSet(collections.MutableMapping):
    """a dict like object that supports merging, patching etc wraps an existing dict"""

    def __init__(self, d):
        """
        really its just a wrapped around an existing dict
        """
        self.store = d
        self.matcher = KeyMatcher.from_dict(d)

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def mega_store(self, other):

        #
        # print "****STORES****"
        # print self.store
        # print other.store
        #

        expanded = deepcopy(self.store)
        for k in self.store.keys():
            if "*" in k:
                matching = other.matcher.get_matching_paths(k)
                for match in matching:
                    expanded[match] = self.store[k]
                # this consumes matched wildcards values
                if matching:
                    del expanded[k]
        mega_store = {}

        for k, v in expanded.iteritems():
            new_key, real_value = value_path_factory(k, v)
            if real_value is not None:
                if not new_key in mega_store.keys():
                    mega_store[new_key] = []
                mega_store[new_key].append(real_value)

        return mega_store


    def _merge_value_array(self, key, values):
        #
        # print ""
        # print "key", key
        #
        # print "************  values  **************\n",
        # #
        # for v in values:
        #     print type(v)
        #     print v

        value_types = set([type(v) for v in values])
        #
        if value_types == {OptionStringWinnowValue, OptionResourceWinnowValue}:
            raise Exception("cant mix strings and resources")


        if len(values) == 1:
            return values[0]
        result = values[0]
        for v in values[1:]:
            result = result.intersection(v)
            if result == None:
                for v in values:
                    print "**********"
                    print "value", type(v)
                    print "keys", v.values_lookup.keys()
                    print utils.json_dumps(v.as_json())
                msg = "The key %s has no possible values when %s are merged" % (key, [v.as_json() for v in values])
                raise OptionsExceptionEmptyOptionValues(msg)

        # if len(value_types) == 1 and {type(result)} != value_types:
        #     print "**********************************************"
        #     print "result: ",  value_types, type(result)

        # if result.as_json() == u"/processes/opendesk/fine-sanding":
        #     print "*************** FUCK **********************"
        #     print key
        #     print values


        return result


    def merge(self, other):
        """
        A union of all keys
        An intersection of values
        """

        # print "***********  merge  **************"
        # print self.store
        # print utils.json_dumps(other.store)
        #

        options = {}
        this_mega_store = self.mega_store(other)
        that_mega_store = other.mega_store(self)
        this_keys = set(this_mega_store.keys())
        that_keys = set(that_mega_store.keys())
        #
        # print this_keys, that_keys

        for key in this_keys.union(that_keys):

            all_values = this_mega_store.get(key, []) + that_mega_store.get(key, [])

            options[key] = self._merge_value_array(key, all_values).as_json()

            # if key == "processes":
            #     print "xxxxxxxxxxxxxxxxxx"
            #     print "self", utils.json_dumps(self.store)
            #     print "other", utils.json_dumps(other.store)
            #
            #     print "result  ",  options[key]

            # print "key", key
            # print "all_values", all_values



        return OptionsSet(options)


    def disallowed_keys(self, other):
        return self._disallowed(other)


    def allows(self, other):
        disallowed = self._disallowed(other)
        print "disallowed", disallowed
        return not bool(disallowed)


    def _disallowed(self, other):
        """
        An intersection of keys
        A subset check on values
        """

        disallowed = []

        this_mega_store = self.mega_store(other)
        that_mega_store = other.mega_store(self)
        this_keys = set(this_mega_store.keys())
        that_keys = set(that_mega_store.keys())

        if this_keys is not None and that_keys is not None:
            all_keys = this_keys.intersection(that_keys)
            if all_keys is not None:
                for key in all_keys:
                    this = self._merge_value_array(key, this_mega_store[key])
                    that = self._merge_value_array(key, that_mega_store[key])
                    if not that.issubset(this):
                        disallowed.append(key)

        return disallowed

    def minimal_default_value(self):
        options = {}
        for k, v in self.store.iteritems():
            options[k] = value_factory(v).get_default()

        return OptionsSet(options)

    def default(self):
        options = {}
        for k, v in self.store.iteritems():
            options[k] = value_factory(v).default

        return OptionsSet(options)

    #
    # def scope(self, scope_name):
    #     """
    #     extracts a subset of options by scope
    #     """
    #     options = {}
    #     for k, v in self.store.iteritems():
    #         if isinstance(v, dict) and u"scopes" in v.keys():
    #             scopes = set(v[u"scopes"])
    #             if not scopes.isdisjoint(set([scope_name])):
    #                 options[k] = deepcopy(v)
    #         else:
    #             options[k] = deepcopy(v)
    #     return OptionsSet(options)


    def match(self, others):
        return [other for other in others if self.allows(other)]


    def reverse_match(self, others):
        return [other for other in others if other.allows(self)]

    @property
    def key_set(self):
        return set(self.store.keys())



