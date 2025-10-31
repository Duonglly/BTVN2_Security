from cryptography.hazmat.primitives.serialization import pkcs12
from endesive import pdf
import datetime

def sign_pdf():
    # --- Đọc file .pfx cá nhân ---
    with open("duongthily.pfx", "rb") as f:
        pfx_data = f.read()

    private_key, cert, add_certs = pkcs12.load_key_and_certificates(
        pfx_data, b"123456"
    )

    # --- Thông tin chữ ký ---
    date = datetime.datetime.utcnow().strftime("D:%Y%m%d%H%M%S+00'00'")
    signature = {
        "sigflags": 3,
        "contact": "Dương Thị Ly",
        "location": "Thai Nguyen University of Technology",
        "signingdate": date,
        "reason": "Bài tập chữ ký số - An toàn và bảo mật thông tin",
        "signature": "Dương Thị Ly",
        "signature_img": "signature.png",   # hình chữ ký .png
        "sigpage": 0,                       # trang đầu
        "sigbutton": True,
        "sigfield": "Signature1",
        "box": (50, 650, 300, 750),    
 
        "text": (
            "Người ký: Dương Thị Ly\n"
            "Ngày ký: 01/11/2025\n"
            "Trường ĐH Kỹ thuật Công nghiệp - TNUT"
        ),
    }

    # --- Đọc file PDF gốc ---
    with open("original.pdf", "rb") as f:
        datau = f.read()

    # --- Ký PDF ---
    datas = pdf.cms.sign(
        datau,
        signature,
        private_key,
        cert,
        add_certs,
        "sha256"
    )

    # --- Ghi file PDF đã ký ---
    with open("signed.pdf", "wb") as f:
        f.write(datau + datas)

    print("✅ Đã ký PDF thành công: signed.pdf")

if __name__ == "__main__":
    sign_pdf()
