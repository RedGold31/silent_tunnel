import os
import json  # превращает Python-словари в JSON-строку
import base64  # переводит байты в текст (а-ля aAB1+CD==)
import jinja2

from dotenv import load_dotenv  # чтобы подгружать переменные из .env файла
from nacl.public import PrivateKey  # библиотека для генерации ключей
from ipaddress import IPv4Network  # помогает разобрать IP-адрес и маску


load_dotenv()

SERVER_ENDPOINT = os.getenv("SERVER_ENDPOINT")
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
    pub = priv.public_key
    return (
        base64.b64encode(bytes(priv)).decode(),
        base64.b64encode(bytes(pub)).decode(),
    )


def make_wg_quick():
    """Создаёт текст wg-quick конфига"""
    tmpl = """[Interface]
PrivateKey = {{peer_priv}}
Jc = {{ JUNK_PACKET_COUNT }}
Jmin = {{ JUNK_PACKET_MIN_SIZE }}
Jmax = {{ JUNK_PACKET_MAX_SIZE }}
S1 = {{ INIT_PACKET_JUNK_SIZE }}
S2 = {{ RESPONSE_PACKET_JUNK_SIZE }}
H1 = {{ INIT_PACKET_MAGIC_HEADER }}
H2 = {{ RESPONSE_PACKET_MAGIC_HEADER }}
H3 = {{ UNDERLOAD_PACKET_MAGIC_HEADER }}
H4 = {{ TRANSPORT_PACKET_MAGIC_HEADER }}
Address = {{ADDRESS}}
DNS = {{DNS}}
MTU = {{MTU}}

[Peer]
PublicKey = {{server_pub}}{% if preshared_key %}\nPresharedKey = {{preshared_key}}{% endif %}
AllowedIPs = {{ALLOWED_IPS}}
Endpoint = {{SERVER_ENDPOINT}}
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
            "addresses": [
                {
                    "address": str(IPv4Network(ADDRESS).network_address),
                    "subnet": str(IPv4Network(ADDRESS).netmask),
                }
            ],
            "dnsServers": DNS.split(", "),
            "jcp": False,  # junk packet count randomization
            "mtu": MTU,
        },
        "peers": [
            {
                "endpoint": SERVER_ENDPOINT,
                "publicKey": server_pub,
                "preSharedKey": preshared_key or "",
                "allowedIps": ALLOWED_IPS.split(", "),
                "persistentKeepalive": 25,
            }
        ],
        "privateKey": peer_priv,
        "publicKey": peer_pub,
    }
    return json.dumps(cfg, indent=2)


def generation(wg: bool = False):
    peer_priv, peer_pub = gen_keypair()
    psk = base64.b64encode(os.urandom(32)).decode()  # можно заменить на фиксированный

    if wg:
        tmp = jinja2.Template(make_wg_quick())
        render = tmp.render(
            peer_priv=peer_priv,
            JUNK_PACKET_COUNT=JUNK_PACKET_COUNT,
            JUNK_PACKET_MIN_SIZE=JUNK_PACKET_MIN_SIZE,
            JUNK_PACKET_MAX_SIZE=JUNK_PACKET_MAX_SIZE,
            INIT_PACKET_JUNK_SIZE=INIT_PACKET_JUNK_SIZE,
            RESPONSE_PACKET_JUNK_SIZE=RESPONSE_PACKET_JUNK_SIZE,
            INIT_PACKET_MAGIC_HEADER=INIT_PACKET_MAGIC_HEADER,
            RESPONSE_PACKET_MAGIC_HEADER=RESPONSE_PACKET_MAGIC_HEADER,
            UNDERLOAD_PACKET_MAGIC_HEADER=UNDERLOAD_PACKET_MAGIC_HEADER,
            TRANSPORT_PACKET_MAGIC_HEADER=TRANSPORT_PACKET_MAGIC_HEADER,
            ADDRESS=ADDRESS,
            DNS=DNS,
            MTU=MTU,
            server_pub=SERVER_PUBLIC_KEY,
            preshared_key=psk,
            ALLOWED_IPS=ALLOWED_IPS,
            SERVER_ENDPOINT=SERVER_ENDPOINT,
        )
        return render
    else:
        return make_amnezia_json(peer_priv, peer_pub, SERVER_PUBLIC_KEY, psk)


if __name__ == "__main__":
    generation()
