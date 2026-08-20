# -*- coding: utf-8 -*-
"""build_language.py — 加密 Language.json -> Language.json.enc.hex (同 Item 流程)
数据源现在是 Language.json 明文本身 (翻译维护在 Gitee 数据仓库, 不再从 C++ 源码提取)
加密算法与 encrypt_item.py / C++ encryptData_ 完全一致 (密钥 m_encryptionByte = 0x6E):
    v4 = key ^ ((key>>1)&8) ^ (2*((key ^ ((key>>1)&8)) & 8))
    out = v4 ^ byte ^ ((v4 & 0x10 ^ 0x6E) >> 1)
异或自反: 同一函数加密两次还原; 输出无换行十六进制
"""
import os

KEY = 0x6E  # m_encryptionByte, 主人确认

OUT_DIR = r'D:\Vsyuanma\genshin-impact-data'
SRC_JSON = os.path.join(OUT_DIR, 'Language.json')
OUT_HEX = SRC_JSON + '.enc.hex'


def compute_v4(key):
    a = key & 0xFF
    b = (a >> 1) & 8
    x = a ^ b
    v4 = (x ^ (2 * (x & 8))) & 0xFF
    return v4


def encrypt_block(data: bytes, key: int) -> bytes:
    v4 = compute_v4(key)
    mask = ((v4 & 0x10 ^ 0x6E) >> 1) & 0xFF
    return bytes((b ^ v4 ^ mask) & 0xFF for b in data)


def main():
    if not os.path.exists(SRC_JSON):
        print('找不到文件:', SRC_JSON)
        print('请先创建 Language.json (格式: {"中文": "英文", ...})')
        input('按回车退出...')
        return

    with open(SRC_JSON, 'rb') as f:
        data = f.read()
    out = encrypt_block(data, KEY)

    with open(OUT_HEX, 'w', encoding='utf-8', newline='') as f:
        f.write(out.hex())
    print('加密完成 -> %s' % OUT_HEX)
    print('hex 长度: %d 字符 (%d 字节)' % (len(out) * 2, len(out)))

    # 校验: 二次运算应还原原文
    check = encrypt_block(out, KEY)
    print('自反校验:', 'OK' if check == data else 'FAIL')
    input('按回车退出...')


if __name__ == '__main__':
    main()
