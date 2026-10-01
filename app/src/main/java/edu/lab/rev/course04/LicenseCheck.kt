package edu.lab.rev.course04

/**
 * 第四课靶场的卡密校验逻辑。
 *
 * 卡密形态：LAB4-XXXX-XXXX，共 8 个有效字符（2 组 x 4），字符集为自定义 Base32。
 * 有效载荷 32 bit：
 *   [31..16] userId     16 bit
 *   [15..4]  expiryDays 12 bit（自 2024-01-01 起的天数偏移）
 *   [3..0]   flags       4 bit（bit0=PRO, bit1=OFFLINE, bit2=LAB, bit3 保留）
 * 校验和 8 bit：FNV-1a 32 位哈希（对 4 字节大端 payload）与盐做异或折叠后的低 8 位。
 * 最终 40 bit = payload(32) || checksum(8)，按自定义字符表（32 字符，每字符 5 bit）编码为 8 个字符。
 */
object LicenseCheck {

    // 去掉了 I/O/0/1 等易混字符的自定义表
    private const val ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    private const val SALT = 0x5A17C0DE.toInt()
    private const val GROUP = 4
    private const val GROUPS = 2

    /** 校验入口。逆向时先找这个函数。 */
    fun isValidKey(raw: String): Boolean {
        val payload = decodePayload(raw) ?: return false
        val (body, checksum) = payload
        if (checksum != checksumOf(body)) return false
        if (flagsOf(body) and 0x4 == 0) return false // 必须带 LAB 位
        return expiryDaysOf(body) > 0
    }

    fun parseKey(raw: String): License? {
        val payload = decodePayload(raw) ?: return null
        val (body, checksum) = payload
        if (checksum != checksumOf(body)) return null
        return License(
            userId = (body ushr 16) and 0xFFFF,
            expiryDays = (body ushr 4) and 0xFFF,
            flags = body and 0xF,
        )
    }

    /** 编码入口，供生成合法卡密的参考实现使用。 */
    fun encodeKey(userId: Int, expiryDays: Int, flags: Int): String {
        val body = ((userId and 0xFFFF) shl 16) or ((expiryDays and 0xFFF) shl 4) or (flags and 0xF)
        val full = (body.toLong() shl 8) or (checksumOf(body).toLong() and 0xFF)
        val chars = (35 downTo 0 step 5).map { shift ->
            val idx = ((full ushr shift) and 0x1F).toInt()
            ALPHABET[idx]
        }.joinToString("")
        return "LAB4-" + chars.chunked(GROUP).take(GROUPS).joinToString("-")
    }

    private fun decodePayload(raw: String): Pair<Int, Int>? {
        val upper = raw.trim().uppercase()
        if (!upper.startsWith("LAB4-")) return null
        val body = upper.removePrefix("LAB4-").replace("-", "")
        if (body.length != GROUP * GROUPS) return null
        if (body.any { it !in ALPHABET }) return null
        var acc = 0L
        for (c in body) {
            val idx = ALPHABET.indexOf(c)
            if (idx < 0) return null
            acc = (acc shl 5) or (idx.toLong() and 0x1F)
        }
        return Pair((acc ushr 8).toInt(), (acc and 0xFF).toInt())
    }

    private fun checksumOf(body: Int): Int {
        var h = 0x811C9DC5.toInt()
        val salt = SALT
        var v = body
        for (i in 0 until 4) {
            h = (h xor ((v ushr 24) and 0xFF)) * 0x01000193
            v = v shl 8
        }
        h = h xor salt
        return (h ushr 8 xor h) and 0xFF
    }

    private fun flagsOf(body: Int) = body and 0xF
    private fun expiryDaysOf(body: Int) = (body ushr 4) and 0xFFF

    data class License(val userId: Int, val expiryDays: Int, val flags: Int)
}
