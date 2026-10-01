#!/usr/bin/env python3
"""第四课靶场卡密校验器 / 生成器。

与 app/src/main/java/edu/lab/rev/course04/LicenseCheck.kt 行为逐位一致，
用于学员在完成逆向后自检自己的还原结果是否正确。

用法:
    python keygen.py gen <userId> <expiryDays> <flags>
    python keygen.py check <KEY>
    python keygen.py selftest
"""

import random
import sys

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
SALT = 0x5A17C0DE
GROUP = 4
GROUPS = 2

MASK32 = 0xFFFFFFFF
MASK40 = 0xFFFFFFFFFF  # payload 32 bit + checksum 8 bit


def checksum_of(body: int) -> int:
    h = 0x811C9DC5
    v = body & MASK32
    for _ in range(4):
        h = ((h ^ ((v >> 24) & 0xFF)) * 0x01000193) & MASK32
        v = (v << 8) & MASK32
    h ^= SALT
    h &= MASK32
    return ((h >> 8) ^ h) & 0xFF


def encode_key(user_id: int, expiry_days: int, flags: int) -> str:
    body = ((user_id & 0xFFFF) << 16) | ((expiry_days & 0xFFF) << 4) | (flags & 0xF)
    full = ((body << 8) | checksum_of(body)) & MASK40
    chars = "".join(ALPHABET[(full >> shift) & 0x1F] for shift in range(35, -1, -5))
    groups = [chars[i:i + GROUP] for i in range(0, len(chars), GROUP)][:GROUPS]
    return "LAB4-" + "-".join(groups)


def decode_payload(raw: str):
    upper = raw.strip().upper()
    if not upper.startswith("LAB4-"):
        return None
    body = upper[len("LAB4-"):].replace("-", "")
    if len(body) != GROUP * GROUPS:
        return None
    acc = 0
    for c in body:
        idx = ALPHABET.find(c)
        if idx < 0:
            return None
        acc = (acc << 5) | idx
    return (acc >> 8) & MASK32, acc & 0xFF


def is_valid_key(raw: str) -> bool:
    p = decode_payload(raw)
    if p is None:
        return False
    body, checksum = p
    if checksum != checksum_of(body):
        return False
    if (body & 0xF) & 0x4 == 0:
        return False
    return ((body >> 4) & 0xFFF) > 0


def parse_key(raw: str):
    p = decode_payload(raw)
    if p is None:
        return None
    body, checksum = p
    if checksum != checksum_of(body):
        return None
    return {
        "userId": (body >> 16) & 0xFFFF,
        "expiryDays": (body >> 4) & 0xFFF,
        "flags": body & 0xF,
    }


def selftest() -> int:
    """三轮确定性验证，任一失败即视为还原有误。

    1) 往返一致性：encode -> check -> parse 必须完全还原输入字段。
    2) 校验和唯一性：固定 payload 时，256 个 checksum 候选中恰好 1 个合法。
       这条能抓住位宽/移位错位——错位会让 0 个或 >1 个候选通过。
    3) 随机串通过率：理论值 (1/256) * (1/2) * (4095/4096)，落在统计区间内。
    """
    random.seed(20240101)
    bad = []

    for _ in range(2000):
        uid = random.randint(0, 0xFFFF)
        days = random.randint(1, 0xFFF)
        flags = random.choice([0x4, 0x5, 0x6, 0x7])
        k = encode_key(uid, days, flags)
        if not is_valid_key(k):
            bad.append(("roundtrip-reject", k, uid, days, flags))
            continue
        lic = parse_key(k)
        if lic != {"userId": uid, "expiryDays": days, "flags": flags}:
            bad.append(("roundtrip-field", k, lic, (uid, days, flags)))

    for _ in range(200):
        uid = random.randint(0, 0xFFFF)
        days = random.randint(1, 0xFFF)
        flags = random.choice([0x4, 0x5, 0x6, 0x7])
        body = ((uid & 0xFFFF) << 16) | ((days & 0xFFF) << 4) | (flags & 0xF)
        hits = 0
        for cs in range(256):
            full = ((body << 8) | cs) & MASK40
            chars = "".join(ALPHABET[(full >> s) & 0x1F] for s in range(35, -1, -5))
            k = "LAB4-" + "-".join(chars[i:i + GROUP] for i in range(0, 8, GROUP))
            if is_valid_key(k):
                hits += 1
                if cs != checksum_of(body):
                    bad.append(("checksum-wrong-slot", k, cs, checksum_of(body)))
        if hits != 1:
            bad.append(("checksum-uniqueness", body, hits))

    n = 20000
    passed = 0
    for _ in range(n):
        k = "LAB4-" + "-".join(
            "".join(random.choice(ALPHABET) for _ in range(GROUP)) for _ in range(GROUPS)
        )
        if is_valid_key(k):
            passed += 1
    expected = n / 256 * 0.5 * (4095 / 4096)
    if not (expected * 0.4 <= passed <= expected * 1.8):
        bad.append(("random-rate", passed, round(expected, 2)))

    print("random-pass rate: %d/%d (expected ~%.1f)" % (passed, n, expected))
    for item in bad[:10]:
        print("FAIL:", item)
    return len(bad)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "gen":
        uid, days, flags = (int(x, 0) for x in sys.argv[2:5])
        key = encode_key(uid, days, flags)
        print(key)
        print(parse_key(key))
        return 0
    if cmd == "check":
        key = sys.argv[2]
        print("valid" if is_valid_key(key) else "invalid", parse_key(key))
        return 0
    if cmd == "selftest":
        bad = selftest()
        print("mismatches:", bad)
        return 1 if bad else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
