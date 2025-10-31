from endesive.pdf import verify

def verify_pdf(pdf_path, cert_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    with open(cert_path, "rb") as f:
        cert = f.read()

    try:
        result = verify(pdf_bytes, (cert,))
        # Trả về 1 dict -> hiển thị chi tiết
        print(" Kết quả xác minh:")
        print(result)
    except Exception as e:
        print("❌ Lỗi xác minh:", e)

if __name__ == "__main__":
    verify_pdf("tampered.pdf", "duongthily.cer")
from endesive.pdf import verify

def verify_pdf(pdf_path, cert_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    with open(cert_path, "rb") as f:
        cert = f.read()

    try:
        result = verify(pdf_bytes, (cert,))
        print("🔍 Kết quả xác minh:")
        print(result)
    except Exception as e:
        print("❌ Lỗi xác minh:", e)

if __name__ == "__main__":
    verify_pdf("signed.pdf", "duongthily.cer")
