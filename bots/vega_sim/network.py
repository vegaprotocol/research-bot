def market_sim_network_from_devops_network_name(net_name: str) -> str:
    mapping = {
        "devnet1": "DEVNET1",
        "stagnet1": "STAGNET1",
        "fairground": "FAIRGROUND",
        "mainnet-mirror": "MAINNET_MIRROR",
        "mainnet_mirror": "MAINNET_MIRROR"
    }

    return mapping[net_name]

