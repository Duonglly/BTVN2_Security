# tamper_pdf.py
# Sửa 1 byte bên trong vùng ByteRange của signed.pdf mà KHÔNG thay đổi kích thước file,
# mục tiêu: làm cho hash & signature bị sai, nhưng vẫn giữ certificate trong /Contents.
#
# Lưu ý: giữ backup trước khi chạy.

import re
import shutil

SIGNED = "signed.pdf"
TAMP = "tampered.pdf"
BACKUP = "signed.backup.pdf"

# 1) tạo bản sao backup
shutil.copyfile(SIGNED, BACKUP)
print(f"Backup tạo: {BACKUP}")

data = None
with open(SIGNED, "rb") as f:
    data = f.read()

# 2) tìm ByteRange: pattern ví dụ /ByteRange [ 0 12345 12345 67890 ]
m = re.search(rb"/ByteRange\s*\[\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\]", data)
if not m:
    raise SystemExit("Không tìm thấy /ByteRange trong file. Kiểm tra file signed.pdf")

a, b, c, d = [int(x) for x in m.groups()]
print(f"ByteRange found: [{a}, {b}, {c}, {d}]")

# 3) Chọn vị trí sửa trong vùng được bảo vệ.
#    Ta tránh sửa trong header PDF quá gần đầu (ví dụ < 200 bytes),
#    và tránh vùng trong /Contents (đã loại ra bởi ByteRange).
#    Sửa trong đoạn đầu (a..a+b) nhưng đảm bảo offset >= a+100.
start = a
end = a + b

# đảm bảo vị trí an toàn
pos = start + 200 if (start + 200) < end else (start + 50 if (start + 50) < end else start)
if pos >= end:
    # nếu không khả thi, chọn trong đoạn thứ hai (c..c+d)
    start = c
    end = c + d
    pos = start + 200 if (start + 200) < end else (start + 50 if (start + 50) < end else start)

if pos >= end:
    raise SystemExit("Không tìm được vị trí an toàn để sửa trong vùng ByteRange.")

print(f"Sẽ sửa 1 byte tại offset: {pos} (trong khoảng [{start}, {end}))")

# 4) sửa 1 byte (XOR với 1) để không thay đổi kích thước file
ba = bytearray(data)
old = ba[pos]
ba[pos] = old ^ 1  # lật 1 bit (thay đổi giá trị nhưng giữ kích thước)
print(f"Byte cũ: {old:#02x} -> Byte mới: {ba[pos]:#02x}")

# 5) ghi file tampered
with open(TAMP, "wb") as f:
    f.write(ba)

print(f"✅ Đã tạo {TAMP}. Chạy verify_pdf.py để kiểm tra (mong ra (False, False, True)).")
