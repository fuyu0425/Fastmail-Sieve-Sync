# https://github.com/fastmail/JMAP-Samples/blob/main/python3/tiny_jmap_library.py
import json
import requests
from typing import Any, Optional
from .sieve import Sieve




class TinyJMAPClient:
    """The tiniest JMAP client you can imagine."""
    def __init__(self, hostname, username, token, cookie):
        """Initialize using a hostname, username and bearer token"""
        assert len(hostname) > 0
        assert len(username) > 0
        assert len(token) > 0
        assert len(cookie) > 0

        self.hostname = hostname
        self.username = username
        self.token = token
        self.cookie = cookie
        self.session = None
        self.api_url = None
        self.account_id = None
        self.identity_id = None
        self.sieve: Optional[Sieve] = None

    def get_session(self):
        """Return the JMAP Session Resource as a Python dict"""
        if self.session:
            return self.session
        r = requests.get(
            "https://" + self.hostname + "/jmap/session",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
                "Cookie": self.cookie
            },
        )
        r.raise_for_status()
        self.session = session = r.json()
        self.api_url = session["apiUrl"]
        return session

    def get_account_id(self):
        """Return the accountId for the account matching self.username"""
        if self.account_id:
            return self.account_id

        session = self.get_session()

        account_id = session["primaryAccounts"]["urn:ietf:params:jmap:mail"]
        self.account_id = account_id
        return account_id

    def get_identity_id(self):
        """Return the identityId for an address matching self.username"""
        if self.identity_id:
            return self.identity_id

        identity_res = self.make_jmap_call({
            "using": [
                "urn:ietf:params:jmap:core",
                "urn:ietf:params:jmap:submission",
            ],
            "methodCalls":
            [["Identity/get", {
                "accountId": self.get_account_id()
            }, "i"]],
        })

        identity_id = next(
            filter(
                lambda i: i["email"] == self.username,
                identity_res["methodResponses"][0][1]["list"],
            ))["id"]

        self.identity_id = str(identity_id)
        return self.identity_id

    def make_jmap_call(self, call):
        """Make a JMAP POST request to the API, returning the response as a
        Python data structure."""
        res = requests.post(
            self.api_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
                "Cookie": self.cookie
            },
            data=json.dumps(call),
        )
        res.raise_for_status()
        return res.json()

    def get_sieve(self):
        if self.sieve: return self.sieve
        if not self.account_id: self.get_account_id()
        get_sieve_res = self.make_jmap_call({
            # it only checks these two using
            "using": [
                "https://www.fastmail.com/dev/rules",
                "https://www.fastmail.com/dev/user",
            ],
            "methodCalls": [[
                "SieveBlocks/get", {
                    "accountId": self.get_account_id(),
                    "ids": ["singleton"]
                }, "0"
            ]],
        })
        sieve_lists = get_sieve_res["methodResponses"][0][1]["list"]
        sieve_dict= sieve_lists[0]
        self.sieve = Sieve(
            require=sieve_dict["sieveRequire"],
            start=sieve_dict["sieveAtStart"],
            blocked=sieve_dict["sieveForBlocked"],
            middle=sieve_dict["sieveAtMiddle"],
            rules=sieve_dict["sieveForRules"],
            end=sieve_dict["sieveAtEnd"],
        )

        return self.sieve

    def set_sieve(self, sieve):
        if not self.account_id: self.get_account_id()
        # we only update start/middle/end
        set_sieve_res = self.make_jmap_call({
            # it only checks these two using
            "using": [
                "https://www.fastmail.com/dev/rules",
                "https://www.fastmail.com/dev/user",
            ],
            "methodCalls": [[
                "SieveBlocks/set", {
                    "accountId": self.get_account_id(),
                    "update": {
                        "singleton": {
                            # NOTE: use raw string
                            "sieveAtStart": sieve._start,
                            "sieveAtMiddle": sieve._middle,
                            "sieveAtEnd": sieve._end,
                        }
                    }
                }, "0"
            ]],
        })

        return set_sieve_res
