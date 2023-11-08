from qwc_services_core.cache import Cache, ExpiringDict, ExpiringEntry


class TestExpiringDict:
    def test_init(self):
        cache = ExpiringDict()
        assert cache.cache == {}

    def test_set(self, mocker):
        mocker.patch("time.time", return_value=300)
        cache = ExpiringDict()
        cache.set("key", "value", 10)
        assert len(cache.cache) == 1
        assert "key" in cache.cache
        assert isinstance(cache.cache["key"], ExpiringEntry)
        assert cache.cache["key"].value == "value"
        assert cache.cache["key"].expires == 310

    def test_lookup(self, mocker):
        mocker.patch("time.time", return_value=300)
        cache = ExpiringDict()
        cache.cache["key"] = ExpiringEntry("value", 600)

        assert cache.lookup("other") == None

        assert cache.lookup("key") == {"value": "value"}
        assert len(cache.cache) == 1

        cache.cache["key"] = ExpiringEntry("value", 200)
        assert cache.lookup("key") == None
        assert len(cache.cache) == 0


class TestCache:
    def test_init(self):
        cache = Cache()
        assert cache.cache == {}

    def test_identity_keys(self):
        assert Cache.identity_keys(None) == [None, "_public_"]
        assert Cache.identity_keys("user") == [None, "user"]
        assert Cache.identity_keys({"username": "user"}) == [None, "user"]
        assert Cache.identity_keys({"username": "user", "group": "group"}) == [
            "group",
            "user",
        ]

    def test_cache_entry(self):
        cache = Cache()
        entry = ExpiringDict()
        entry.set("key2", "value", 200)
        cache.cache["service"] = {"group": {"user": {"key1": entry}}}
        assert cache.cache_entry(
            "service", {"username": "user", "group": "group"}, ("key1", "key2")
        ) == (entry, "key2")

    def test_read(self, mocker):
        mocker.patch("time.time", return_value=300)
        cache = Cache()
        entry = ExpiringDict()
        entry.set("key2", "value", 200)
        cache.cache["service"] = {"group": {"user": {"key1": entry}}}
        assert (
            cache.read(
                "service", {"username": "user", "group": "group"}, ("key1", "key2")
            )
            == "value"
        )
        assert (
            cache.read(
                "service", {"username": "user", "group": "group"}, ("key1", "lorem")
            )
            is None
        )

        entry.set("key3", "value", 0)
        assert (
            cache.read(
                "service", {"username": "user", "group": "group"}, ("key1", "key3")
            )
            is None
        )

    def test_write(self, mocker):
        mocker.patch("time.time", return_value=300)
        cache = Cache()
        cache.write(
            "service",
            {"username": "user", "group": "group"},
            ("key1", "key2"),
            "value",
            200,
        )
        assert len(cache.cache) == 1
        assert "service" in cache.cache
        assert len(cache.cache["service"]) == 1
        assert "group" in cache.cache["service"]
        assert len(cache.cache["service"]["group"]) == 1
        assert "user" in cache.cache["service"]["group"]
        assert len(cache.cache["service"]["group"]["user"]) == 1
        assert "key1" in cache.cache["service"]["group"]["user"]
        exp_dict = cache.cache["service"]["group"]["user"]["key1"]
        assert isinstance(exp_dict, ExpiringDict)
        assert len(exp_dict.cache) == 1
        assert "key2" in exp_dict.cache
        assert exp_dict.lookup("key2") == {"value": "value"}
