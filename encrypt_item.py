# -*- coding: utf-8 -*-
"""encrypt_item.py — 用 genshin 的 encryptData_ 算法加密/解密 Item.json
算法复刻(与 C++ 一致, 有符号 char 按 int 模拟后 &0xFF):
    v4   = key ^ ((key>>1)&8) ^ (2*((key ^ ((key>>1)&8)) & 8))
    out  = v4 ^ byte ^ ((v4 & 0x10 ^ 0x6E) >> 1)
密钥 m_encryptionByte = 0x6E (主人确认)
异或自反: 同一函数加密两次还原, 所以 encrypt/decrypt 相同
"""
import sys, os

KEY = 0x6E  # m_encryptionByte, 主人确认

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
    src = r'D:\Vsyuanma\genshin-impact-data\Item.json'
    # 目标文件: 默认 Item.json.enc; 传 --dec 或文件名参数可改
    if len(sys.argv) > 1 and sys.argv[1] in ('--dec', '--enc'):
        mode = sys.argv[1][2:]
    else:
        mode = 'enc'
    dst = src + ('.dec' if mode == 'dec' else '.enc')

    if not os.path.exists(src):
        print('找不到文件:', src)
        sys.exit(1)

    with open(src, 'rb') as f:
        data = f.read()
    out = encrypt_block(data, KEY)
    with open(dst, 'wb') as f:
        f.write(out)
    print('%s %s -> %s  (%d bytes)' % ('加密' if mode == 'enc' else '解密', src, dst, len(out)))
    # 校验: 二次运算应还原原文
    check = encrypt_block(out, KEY)
    print('自反校验:', 'OK' if check == data else 'FAIL')

if __name__ == '__main__':
    main()
