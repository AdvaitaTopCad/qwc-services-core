"""Time-aware caches."""
import copy
import time
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union

from attrs import define, field
from typing_extensions import TypedDict

T = TypeVar("T")

# Special user name for public access.
PUBLIC_USER = "_public_"


@define
class ExpiringEntry(Generic[T]):
    """Entry for ExpiringDict.

    Attributes:
        value: Cached value.
        expires: Expiry time in seconds.
    """

    value: T
    expires: float


class CacheResult(TypedDict, Generic[T]):
    """Result of Cache.lookup().

    Attributes:
        value: Cached value.
    """

    value: T


@define
class ExpiringDict(Generic[T]):
    """Dict for values where each key will expire after some time.

    Note:
        The values are only removed when they are accessed after the expiry
        time. The time is retrieved with ``time.time()``.

    Attributes:
        cache: Dict with cached values
    """

    cache: Dict[str, ExpiringEntry[T]] = field(factory=dict, init=False)

    def set(self, key: str, value: T, duration: float = 300):
        """Store value under key until the timeout expires.

        Args:
            key: The key for value.
            value: The value to store (will be deep-cloned).
            duration: Time in seconds until expiry (default: 300s).
        """
        self.cache[key] = ExpiringEntry(
            value=copy.deepcopy(value), expires=time.time() + duration
        )

    def lookup(self, key: str) -> Optional[CacheResult[T]]:
        """Return dict with value or None if not present or expired.

        Args:
            key: Key for value

        Returns:
          {'value': <value>} or None
        """
        res: Optional[CacheResult[T]] = None

        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry.expires:
                res = {"value": copy.deepcopy(entry.value)}
            else:
                # remove expired value
                del self.cache[key]

        return res


class Identity(TypedDict):
    """Identity dict for user name and group.

    Attributes:
        username: User name.
        group: Group name.
    """

    username: str
    group: str


@define
class Cache:
    """Nested dict for values where each leaf key will expire after some time.

    The cache consists of the following levels:
    - service
    - group
    - user
    - key
    - ...
    - key: ExpiringDict

    Attributes:
        cache: Dict with cached values
    """

    cache: Dict[str, Any] = field(factory=dict, init=False)

    def init(self):
        """(Re-)Initialize cache."""
        self.cache = {}

    @staticmethod
    def identity_keys(identity: Union[str, Identity]) -> List[Optional[str]]:
        """Get group and username from identity.

        Args:
            identity: User name or Identity dict.

        Returns:
            [group, username] for identity.
        """
        if identity is not None:
            if isinstance(identity, dict):
                return [identity.get("group"), identity.get("username")]
            else:
                # identity is username
                return [None, identity]
        else:
            # keys for empty user
            return [None, PUBLIC_USER]

    def cache_entry(
        self,
        service: str,
        identity: Union[str, Identity],
        keys: Union[tuple, List[str]],
    ) -> Tuple[ExpiringDict[Any], str]:
        """Locate cache entry for service, identity and keys.

        Args:
            service: Service name.
            identity: User name or Identity dict.
            keys: List of keys.

        Returns:
            Tuple of ``(cache, key)`` where ``key`` is the they inside
            the cache (last argument provided).
        """
        # cache is a nested dict with the following levels:
        cache_keys = [service] + self.identity_keys(identity) + list(keys)
        # print("cache_entry %s" % cache_keys)
        cache = self.cache

        # Read or initialize cache level by level.
        for key in cache_keys[:-2]:
            entry = cache.get(key)
            if entry is None:
                entry = {}
                cache[key] = entry
            cache = entry

        # Second last key points to ExpiringDict cache entry.
        key = cache_keys[-2]
        entry = cache.get(key)
        if entry is None:
            entry = ExpiringDict()
            cache[key] = entry

        # Last key points to ExpiringEntry cache entry.
        key = cache_keys[-1]
        return (entry, key)

    def read(
        self,
        service: str,
        identity: Union[str, Identity],
        keys: Union[tuple, List[str]],
    ):
        """Read value from cache.

        Args:
            service: Service name.
            identity: User name or Identity dict.
            keys: List of keys.

        Returns:
            Cached value or None if not present or expired.
        """
        cache, key = self.cache_entry(service, identity, keys)
        entry = cache.lookup(key)
        if entry:
            # print("Reading data from cache with key '%s'" % key)
            return entry["value"]
        else:
            return None

    def write(
        self,
        service: str,
        identity: Union[str, Identity],
        keys: Union[tuple, List[str]],
        data: Any,
        cache_duration: float = 300,
    ):
        """Write value into cache.

        Args:
            service: Service name.
            identity: User name or Identity dict.
            keys: List of keys.
            data: Value to store.
            cache_duration: Time in seconds until expiry.
        """
        cache, key = self.cache_entry(service, identity, keys)
        # print("Writing data into cache with key '%s'" % key)
        cache.set(key, data, cache_duration)
