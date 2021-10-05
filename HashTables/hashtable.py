"""
Joan Chirinos

My own implementation of a HashTable

Search: θ(1), O(n)
    Because our hash table uses buckets, it's possible (though unlikely) that
    we will have to go through all n elements in the hash table if they all end
    up in the same bucket.
    However, with a good hash function it will average linear time.

Insertion: θ(1), O(n)
    We only need linear time when the hash table meets the load factor and we
    must rehash. Otherwise, with a good hash function it will average linear
    time.

Deletion: θ(1), O(n)
    Again, a good hash function will average linear time. If all keys fall
    into one bucket, we will pop an item from a length-n list, which is O(n)

Space: O(n)
    Do note, however, that this implementation doubles the internal array size
    upon hitting the load factor. Thus, the space usage will jump rather than
    slowly grow.

We use a deque from collections to store a stack of keys that have been entered
into the hash table.
This allows for O(1) insertion and deletion, but likely uses more space than a
list(?).
This is exclusively used for popitem. Though the specification says I
should implement popitem, I don't like it. I'm sure I just haven't come across
use cases for it, but it seems weird.
"""

from __future__ import annotations
from typing import Sequence, Callable, Any, List, Hashable, Optional, Tuple
from collections import deque


class HashTable:
    """HashTable with the usual methods"""

    def __init__(self, initial_capacity: int = 100, load_factor: float = 0.75,
                 hash_function: Callable[[Hashable], int] = hash) -> None:
        """
        Create a HashTable from given parameters

        Parameters
        ----------
        initial_capacity : int
            initial length of internal array (the default is 100).
        load_factor : float
            ratio at which HashTable should be resized (the default is 0.75).
        hash_function : Callable[[Hashable], int]
            the hash function (the default is hash).

        Returns
        -------
        None

        """
        self.array = [[] for i in range(initial_capacity)]
        self.hash_function = hash
        self.size = 0
        self.internal_array_size = initial_capacity
        self.load_factor = load_factor
        self.stack = deque()

    def clear(self) -> None:
        """
        Clear HashTable.

        Returns
        -------
        None.

        """
        self.array = [[] for i in range(self.internal_array_size)]
        self.stack = deque()
        self.size = 0

    def copy(self) -> HashTable:
        """
        Return shallow copy of HashTable

        Returns
        -------
        HashTable
            shallow copy of HashTable.

        """
        pairs = self.items()
        new_hash_table = HashTable()
        for k, v in pairs:
            new_hash_table[k] = v
        return new_hash_table

    @classmethod
    def fromkeys(cls, keys: Sequence[Hashable], val: Optional[Any] = None,
                 initial_capacity: int = 100, load_factor: float = 0.75,
                 hash_function: Callable[[Hashable], int] = hash) -> HashTable:
        """
        Generate HashTable from Sequence of keys and default value

        Parameters
        ----------
        keys : Sequence[Hashable]
            Sequence of keys from which to generate HashTable
        val : Optional[Any]
            default value for every key (the default is None).
        initial_capacity : int
            initial length of internal array (the default is 100).
        load_factor : float
            ratio at which HashTable should be resized (the default is 0.75).
        hash_function : Callable[[Hashable], int]
            the hash function (the default is hash).

        Returns
        -------
        HashTable
            HashTable with specified keys and default value.

        """
        ht = cls(initial_capacity, load_factor, hash_function)
        for key in keys:
            ht[key] = val
        return ht

    def get(self, key: Hashable) -> Any:
        """
        Get value for specified key in HashTable.

        Parameters
        ----------
        key : Hashable
            the key.

        Returns
        -------
        Any
            The value corresponding to the key in HashTable.
            None if key not in HashTable.

        """
        i = self.__key_to_index(key)
        bucket = self.array[i]
        for k, v in bucket:
            if k == key:
                return v
        return None

    def put(self, key: Hashable, value: Any) -> Any:
        """
        Add key, value pair to HashTable.

        Parameters
        ----------
        key : Hashable
            the key
        value : Any
            the value

        Returns
        -------
        Any
            The previous value corresponding to the key.
            None if no previous value in HashTable.

        """
        old_value = self.pop(key)
        self.__rehash()
        i = self.__key_to_index(key)
        self.array[i].append((key, value))
        if old_value is not None:
            self.size += 1
        self.stack.append(key)
        return old_value

    def items(self) -> List[Tuple[Hashable, Any]]:
        """
        Return a List of all (key, value) tuples in HashTable.

        Returns
        -------
        List[Tuple[Hashable, Any]]
            a List of (key, value) tuples in the HashTable.

        """
        item_list = []
        for bucket in self.array:
            for pair in bucket:
                item_list.append(pair)
        return item_list

    def keys(self) -> List[Hashable]:
        """
        Return List of HashTable's keys

        Returns
        -------
        List[Hashable]
            List of HashTable's keys

        """
        return list(map(lambda x: x[0], self.items()))

    def pop(self, key: Hashable) -> Any:
        """
        Remove the key and corresponding value from HashTable.

        Parameters
        ----------
        key : Hashable
            the key.

        Returns
        -------
        Any
            the corresponding value, before removal.

        """
        a = self.__key_to_index(key)
        for b in range(len(self.array[a])):
            if self.array[a][b][0] == key:
                _, v = self.array[a].pop(b)
                self.size -= 1
                return v
        return None

    def popitem(self) -> Any:
        """
        Return the last item inserted into HashTable.

        Returns
        -------
        Any
            the last item inserted into HashTable.

        Raises
        -------
        TypeError
            If HashTable is empty.

        """
        while True:
            if len(self.stack) == 0:
                raise TypeError('HashTable is empty')
            k = self.stack.pop()
            v = self.pop(k)
            if v is not None:
                return v

    def setdefault(self, key: Hashable, value: Optional[Any] = None) -> Any:
        """
        Return value of specified key, or set default value to key.

        Parameters
        ----------
        key : Hashable
            the key.
        value : Optional[Any]
            the default value (the default is None).

        Returns
        -------
        Any
            the value associated with the key in HashTable

        """
        if self[key] is None:
            self[key] = value
        return self[key]

    def values(self) -> List[Any]:
        """
        Return list of all values in HashTable.

        Returns
        -------
        List[Any]
            list of all values in HashTable.

        """
        return list(map(lambda x: x[1], self.items()))

    def contains_value(self, value: Any) -> bool:
        """
        Return whether or not HashTable contains the specified value.

        Parameters
        ----------
        value : Any
            the value.

        Returns
        -------
        bool
            True if HashTable contains the specified value, False otherwise.

        """
        for bucket in self.array:
            for _, v in bucket:
                if v == value:
                    return True
        return False

    def contains_key(self, key: Hashable) -> bool:
        """
        Return whether or not HashTable maps to the specified key.

        Parameters
        ----------
        key : Hashable
            the key.

        Returns
        -------
        bool
            True if HashTable maps to the specified key, False otherwise.

        """
        i = self.__key_to_index(key)
        bucket = self.array[i]
        return len(bucket) >= 1

    def __key_to_index(self, key: Hashable) -> int:
        """
        Return the index in the HashTable corresponding to the specified key

        Parameters
        ----------
        key : Hashable
            the key.

        Returns
        -------
        int
            the index in the HashTable for the specified key.

        """
        return self.hash_function(key) % self.internal_array_size

    def __rehash(self) -> None:
        """
        Rehash the HashTable once load factor has been reached.

        Returns
        -------
        None

        """
        if self.size < len(self.array) * self.load_factor:
            return
        new_array = [[] for i in range(self.internal_array_size * 2)]
        for i in self.array:
            for k, v in i:
                i = self.hash_function(k) % (2 * self.internal_array_size)
                new_array[i].append((k, v))
        self.array = new_array
        self.internal_array_size *= 2

    def __getitem__(self, key: Hashable) -> Any:
        """
        x.__getitem__(y) <==> x[y]
        """
        return self.get(key)

    def __setitem__(self, key: Hashable, value: Any) -> Any:
        """
        Set self[key] to value.
        """
        return self.put(key, value)

    def __contains__(self, key: Hashable) -> bool:
        """True if HashTable has the specified key, False if not"""
        return self.contains_key(key)

    def __len__(self) -> int:
        """
        Return len(self).
        """
        return self.size

    def __iter__(self):
        """Return iter(self.keys())"""
        return iter(self.keys())

    def __repr__(self):
        """Return dict-like representation of HashTable"""
        pairs = map(lambda x: '{}: {}'.format(repr(x[0]), repr(x[1])),
                    self.items())
        return '{' + ', '.join(pairs) + '}'


if __name__ == "__main__":
    a = HashTable()
    for i in range(10):
        a[i] = i * i
    a[5] = 1000
    a[2] = 4000
    print(repr(a))
    while True:
        print(a.popitem())
