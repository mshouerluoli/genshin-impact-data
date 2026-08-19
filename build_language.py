# -*- coding: utf-8 -*-
"""build_language.py — 从 Language.cpp 提取翻译表, 生成 Language.json + Language.json.enc.hex
加密算法与 encrypt_item.py / C++ encryptData_ 完全一致 (密钥 m_encryptionByte = 0x6E):
    v4 = key ^ ((key>>1)&8) ^ (2*((key ^ ((key>>1)&8)) & 8))
    out = v4 ^ byte ^ ((v4 & 0x10 ^ 0x6E) >> 1)
异或自反: 同一函数加密两次还原; 输出无换行十六进制
"""
import json
import os
import re

KEY = 0x6E  # m_encryptionByte, 主人确认

SRC_CPP = r'D:\Vsyuanma\genshin-impact-version\version\Language\Language.cpp'
OUT_DIR = r'D:\Vsyuanma\genshin-impact-data'
OUT_JSON = os.path.join(OUT_DIR, 'Language.json')
OUT_HEX = OUT_JSON + '.enc.hex'


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


def extract_translations(cpp_path: str):
    """从 Language.cpp 提取 {(char*)u8"中文", "英文"} 翻译对, 保持源文件顺序"""
    with open(cpp_path, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8-sig')  # 源文件带 BOM
    pattern = re.compile(r'\{\s*\(char\*\)u8"([^"]+)",\s*"([^"]+)"\s*\}')
    pairs = pattern.findall(text)
    return pairs


def main():
    if not os.path.exists(SRC_CPP):
        print('找不到文件:', SRC_CPP)
        input('按回车退出...')
        return

    pairs = extract_translations(SRC_CPP)
    print('提取翻译条目: %d' % len(pairs))

    # 统计重复中文 key (C++ unordered_map 语义: 后者覆盖前者, JSON dict 同样)
    seen = {}
    dup = []
    for zh, en in pairs:
        if zh in seen:
            dup.append((zh, seen[zh], en))
        seen[zh] = en

    if dup:
        print('重复 key %d 个 (JSON 以最后一个为准, 与 C++ map 一致):' % len(dup))
        for zh, old, new in dup:
            print('  "%s": "%s" -> "%s"' % (zh, old, new))
    else:
        print('无重复 key')

    # 写 Language.json (2 空格缩进, 与 Item.json 风格一致, CRLF 结尾)
    with open(OUT_JSON, 'w', encoding='utf-8', newline='') as f:
        f.write(json.dumps(seen, ensure_ascii=False, indent=2).replace('\n', '\r\n') + '\r\n')
    print('JSON 生成 -> %s (%d 条)' % (OUT_JSON, len(seen)))

    # 加密 -> hex
    with open(OUT_JSON, 'rb') as f:
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
