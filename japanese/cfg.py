def load():
    try:
        from aqt import mw
        return mw.addonManager.getConfig(__name__)
    except AttributeError:
        # unit test
        import os, json
        dir = os.path.dirname(__file__)
        path = os.path.join(dir, "config.json")
        return json.load(open(path))
