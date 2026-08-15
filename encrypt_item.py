# -*- coding: utf-8 -*-
"""encrypt_item.py — 用 genshin 的 encryptData_ 算法加密 Item.json, 只输出 hex
算法复刻(与 C++ 一致, 有符号 char 按 int 模拟后 &0xFF):
    v4   = key ^ ((key>>1)&8) ^ (2*((key ^ ((key>>1)&8)) & 8))
    out  = v4 ^ byte ^ ((v4 & 0x10 ^ 0x6E) >> 1)
密钥 m_encryptionByte = 0x6E (主人确认)
异或自反: 同一函数加密两次还原
运行: 生成 Item.json.enc.hex(无换行十六进制, 链接打开不乱码)
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
    if not os.path.exists(src):
        print('找不到文件:', src)
        input('按回车退出...')
        sys.exit(1)

    with open(src, 'rb') as f:
        data = f.read()
    out = encrypt_block(data, KEY)

    hex_path = src + '.enc.hex'
    with open(hex_path, 'w', encoding='utf-8') as f:
        f.write(out.hex())
    print('加密完成 -> %s' % hex_path)
    print('hex 长度: %d 字符 (%d 字节)' % (len(out) * 2, len(out)))

    # 校验: 二次运算应还原原文
    check = encrypt_block(out, KEY)
    print('自反校验:', 'OK' if check == data else 'FAIL')
    input('按回车退出...')

if __name__ == '__main__':
    main()
