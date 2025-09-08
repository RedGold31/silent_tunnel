import os
import json             # превращает Python-словари в JSON-строку
import base64           # переводит байты в текст (а-ля aAB1+CD==)
import argparse         # чтобы скрипт понимал параметры командной строки
from dotenv import load_dotenv      # чтобы подгружать переменные из .env файла
from nacl.public import PrivateKey  # библиотека для генерации ключей
from ipaddress import IPv4Network   # помогает разобрать IP-адрес и маску

load_dotenv()

SERVER_ENDPOINT   = os.getenv("SERVER_ENDPOINT")
SERVER_PUBLIC_KEY = os.getenv("SERVER_PUBLIC_KEY")
ALLOWED_IPS = os.getenv("ALLOWED_IPS")
ADDRESS = os.getenv("ADDRESS")
DNS = os.getenv("DNS")
MTU = os.getenv("MTU")
JUNK_PACKET_COUNT = os.getenv("JUNK_PACKET_COUNT")
JUNK_PACKET_MIN_SIZE = os.getenv("JUNK_PACKET_MIN_SIZE")
JUNK_PACKET_MAX_SIZE = os.getenv("JUNK_PACKET_MAX_SIZE")
INIT_PACKET_JUNK_SIZE = os.getenv("INIT_PACKET_JUNK_SIZE")
RESPONSE_PACKET_JUNK_SIZE = os.getenv("RESPONSE_PACKET_JUNK_SIZE")
INIT_PACKET_MAGIC_HEADER = os.getenv("INIT_PACKET_MAGIC_HEADER")
RESPONSE_PACKET_MAGIC_HEADER = os.getenv("RESPONSE_PACKET_MAGIC_HEADER")
UNDERLOAD_PACKET_MAGIC_HEADER = os.getenv("UNDERLOAD_PACKET_MAGIC_HEADER")
TRANSPORT_PACKET_MAGIC_HEADER = os.getenv("TRANSPORT_PACKET_MAGIC_HEADER")

def gen_keypair():
    """Возвращает (base64_private, base64_public)"""
    priv = PrivateKey.generate()
    pub  = priv.public_key
    return (
        base64.b64encode(bytes(priv)).decode(),
        base64.b64encode(bytes(pub)).decode()
    )

def make_wg_quick(peer_priv, peer_pub, server_pub, preshared_key=None):
    """Создаёт текст wg-quick конфига"""
    tmpl = f"""[Interface]
PrivateKey = {peer_priv}
Address = {ADDRESS}
DNS = {DNS}
MTU = {MTU}

[Peer]
PublicKey = {server_pub}
PresharedKey = {preshared_key or ""}
AllowedIPs = {ALLOWED_IPS}
Endpoint = {SERVER_ENDPOINT}
PersistentKeepalive = 25
"""
    return tmpl

def make_amnezia_json(peer_priv, peer_pub, server_pub, preshared_key=None):
    """Создаёт JSON, который понимает AmneziaVPN"""
    # ключи AWG хранятся в том же base64, что и WG
    cfg = {
        "h1": INIT_PACKET_MAGIC_HEADER,
        "h2": RESPONSE_PACKET_MAGIC_HEADER,
        "h3": UNDERLOAD_PACKET_MAGIC_HEADER,
        "h4": TRANSPORT_PACKET_MAGIC_HEADER,
        "jc": JUNK_PACKET_COUNT,
        "jmin": JUNK_PACKET_MIN_SIZE,
        "jmax": JUNK_PACKET_MAX_SIZE,
        "s1": INIT_PACKET_JUNK_SIZE,
        "s2": RESPONSE_PACKET_JUNK_SIZE,
        "interface": {
            "addresses": [{"address": str(IPv4Network(ADDRESS).network_address),
                           "subnet": str(IPv4Network(ADDRESS).netmask)}],
            "dnsServers": DNS.split(", "),
            "jcp": False,      # junk packet count randomization
            "mtu": MTU
        },
        "peers": [{
            "endpoint": SERVER_ENDPOINT,
            "publicKey": server_pub,
            "preSharedKey": preshared_key or "",
            "allowedIps": ALLOWED_IPS.split(", "),
            "persistentKeepalive": 25
        }],
        "privateKey": peer_priv,
        "publicKey": peer_pub
    }
    return json.dumps(cfg, indent=2)

def generation():
    ap = argparse.ArgumentParser(description="AmneziaWG client config generator")
    ap.add_argument("--wg", action="store_true", help="Выдать wg-quick вместо JSON")
    args = ap.parse_args()

    peer_priv, peer_pub = gen_keypair()
    psk = base64.b64encode(os.urandom(32)).decode()   # можно заменить на фиксированный

    if args.wg:
        with open(f'vpn/configs/config.conf', 'w', encoding='UTF=8') as f:
            f.write(make_wg_quick(peer_priv, peer_pub, SERVER_PUBLIC_KEY, psk))
        print(make_wg_quick(peer_priv, peer_pub, SERVER_PUBLIC_KEY, psk))
    else:
        with open(f'vpn/configs/config.conf', 'w', encoding='UTF=8') as f:
            f.write(make_amnezia_json(peer_priv, peer_pub, SERVER_PUBLIC_KEY, psk))
        print(make_amnezia_json(peer_priv, peer_pub, SERVER_PUBLIC_KEY, psk))

if __name__ == "__main__":
    generation()