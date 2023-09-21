import os
import json
import multiprocessing


from dataclasses import dataclass


def default_wallet_struct(public_key: str, recovery_passphrase: str) -> dict:
    return {
        "public_key": public_key,
        "recovery_phrase": recovery_passphrase,
        "keys": {},
    }

def default_key_struct(name: str, public_key: str, index: int) -> dict:
    return {
        "name": name,
        "public_key": public_key,
        "index": index,
    }

@dataclass
class KeyState:
    name: str
    public_key: str
    index: int

@dataclass
class WalletState:
    name: str
    public_key: str
    recovery_phrase: str
    keys: dict[str, KeyState]

VegaWalletStateType = dict[str, WalletState]


def vega_wallet_state_from_json(json: dict) -> VegaWalletStateType:
    wallets = json.get("wallets", {})

    result = VegaWalletStateType()

    for wallet_name in wallets:
        result[wallet_name] = WalletState(
            name = wallet_name,
            public_key = wallets[wallet_name].get("public_key", ""),
            recovery_phrase = wallets[wallet_name].get("recovery_phrase", ""),
            keys = {},
        )

        keys = wallets[wallet_name].get("keys", {})

        for public_key in keys:
            result[wallet_name].keys[public_key] = KeyState(
                public_key = public_key,
                name = keys[public_key].get("name", ""),
                index = keys[public_key].get("index", 0),
            )

    return result
        

def vega_wallet_state_from_file(path: str) -> VegaWalletStateType:
    if not os.path.exists(path):
        return VegaWalletStateType()
    
    with open(path, "r") as file:
        state = json.load(file)
        return vega_wallet_state_from_json(state)

class WalletStateService:
    def __init__(self, path: str):
        self._path = path
        self._mutex = multiprocessing.Lock()

    
    def _load_state(self) -> dict:
        state = {}

        if os.path.exists(self._path):
            with open(self._path, "r") as file:
                state = json.load(file)

        return state

    def _save_state(self, state: dict):
        json_object = json.dumps(state, indent=4)
        
        with open(self._path, "w+") as outfile:
            outfile.write(json_object)
    

    def add_wallet(self, wallet_name: str, public_key: str, recovery_phrase: str):
        with self._mutex:
            state = self._load_state()

            if "wallets" not in state:
                state["wallets"] = {}
            
            state["wallets"][wallet_name] = default_wallet_struct(
                public_key, 
                recovery_phrase,
            )

            self._save_state(state)


    def add_key(self, wallet_name: str, key_name: str, public_key: str, index: int):
        with self._mutex:
            state = self._load_state()
            if not "wallets" in state:
                state["wallets"] = {}
            
            if not wallet_name in state["wallets"]:
                state["wallets"][wallet_name] = default_wallet_struct("", "")

            state["wallets"][wallet_name]["keys"][public_key] = default_key_struct(key_name, public_key, index)
            self._save_state(state)
    
    def state_as_json(self) -> dict:
        with self._mutex:
            return self._load_state()
    
    def state_as_struct(self) -> VegaWalletStateType:
        return vega_wallet_state_from_json(self.state_as_json())