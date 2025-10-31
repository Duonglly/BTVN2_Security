# BTVN2_Security
BÀI TẬP VỀ NHÀ – MÔN: AN TOÀN VÀ BẢO MẬT THÔNG TIN
Chủ đề: Chữ ký số trong file PDF
Giảng viên: Đỗ Duy Cốp
Thời điểm giao: 2025-10-24 11:45
Đối tượng áp dụng: Toàn bộ sv lớp học phần 58KTPM
Hạn nộp: Sv upload tất cả lên github trước 2025-10-31 23:59:59
---
I. MÔ TẢ CHUNG
Sinh viên thực hiện báo cáo và thực hành: phân tích và hiện thực việc nhúng, xác
thực chữ ký số trong file PDF.
Phải nêu rõ chuẩn tham chiếu (PDF 1.7 / PDF 2.0, PAdES/ETSI) và sử dụng công cụ
thực thi (ví dụ iText7, OpenSSL, PyPDF, pdf-lib).
---
II. CÁC YÊU CẦU CỤ THỂ
1) Cấu trúc PDF liên quan chữ ký (Nghiên cứu)
- Mô tả ngắn gọn: Catalog, Pages tree, Page object, Resources, Content streams,
XObject, AcroForm, Signature field (widget), Signature dictionary (/Sig),
/ByteRange, /Contents, incremental updates, và DSS (theo PAdES).
- Liệt kê object refs quan trọng và giải thích vai trò của từng object trong
lưu/truy xuất chữ ký.
- Đầu ra: 1 trang tóm tắt + sơ đồ object (ví dụ: Catalog → Pages → Page → /Contents
; Catalog → /AcroForm → SigField → SigDict).
2) Thời gian ký được lưu ở đâu?
- Nêu tất cả vị trí có thể lưu thông tin thời gian:
 + /M trong Signature dictionary (dạng text, không có giá trị pháp lý).
 + Timestamp token (RFC 3161) trong PKCS#7 (attribute timeStampToken).
 + Document timestamp object (PAdES).
 + DSS (Document Security Store) nếu có lưu timestamp và dữ liệu xác minh.
- Giải thích khác biệt giữa thông tin thời gian /M và timestamp RFC3161.
3) Các bước tạo và lưu chữ ký trong PDF (đã có private RSA)
- Viết script/code thực hiện tuần tự:
 1. Chuẩn bị file PDF gốc.
 2. Tạo Signature field (AcroForm), reserve vùng /Contents (8192 bytes).
 3. Xác định /ByteRange (loại trừ vùng /Contents khỏi hash).
 4. Tính hash (SHA-256/512) trên vùng ByteRange.
 5. Tạo PKCS#7/CMS detached hoặc CAdES:
 - Include messageDigest, signingTime, contentType.
 - Include certificate chain.
 - (Tùy chọn) thêm RFC3161 timestamp token.
 6. Chèn blob DER PKCS#7 vào /Contents (hex/binary) đúng offset.
 7. Ghi incremental update.
 8. (LTV) Cập nhật DSS với Certs, OCSPs, CRLs, VRI.
- Phải nêu rõ: hash alg, RSA padding, key size, vị trí lưu trong PKCS#7.
- Đầu ra: mã nguồn, file PDF gốc, file PDF đã ký.
4) Các bước xác thực chữ ký trên PDF đã ký
- Các bước kiểm tra:
 1. Đọc Signature dictionary: /Contents, /ByteRange.
 2. Tách PKCS#7, kiểm tra định dạng.
 3. Tính hash và so sánh messageDigest.
 4. Verify signature bằng public key trong cert.
 5. Kiểm tra chain → root trusted CA.
 6. Kiểm tra OCSP/CRL.
 7. Kiểm tra timestamp token.
 8. Kiểm tra incremental update (phát hiện sửa đổi).
- Nộp kèm script verify + log kiểm thử.
---
III. YÊU CẦU NỘP BÀI
1. Báo cáo PDF ≤ 6 trang: mô tả cấu trúc, thời gian ký, rủi ro bảo mật.
2. Code + README (Git repo hoặc zip).
3. Demo files: original.pdf, signed.pdf, tampered.pdf.
4. (Tuỳ chọn) Video 3–5 phút demo kết quả.
---
IV. TIÊU CHÍ CHẤM
- Lý thuyết & cấu trúc PDF/chữ ký: 25%
- Quy trình tạo chữ ký đúng kỹ thuật: 30%
- Xác thực đầy đủ (chain, OCSP, timestamp): 25%
- Code & demo rõ ràng: 15%
- Sáng tạo mở rộng (LTV, PAdES): 5%
---
V. GHI CHÚ AN TOÀN
- Vẫn lưu private key (sinh random) trong repo. Tránh dùng private key thương mại.
- Dùng RSA ≥ 2048-bit và SHA-256 hoặc mạnh hơn.
- Có thể dùng RSA-PSS thay cho PKCS#1 v1.5.
- Khuyến khích giải thích rủi ro: padding oracle, replay, key leak.
---
VI. GỢI Ý CÔNG CỤ
- OpenSSL, iText7/BouncyCastle, pypdf/PyPDF2.
- Tham khảo chuẩn PDF: ISO 32000-2 (PDF 2.0) và ETSI EN 319 142 (PAdES).

  # Trình Bày

  # Cấu trúc PDF liên quan chữ ký

  ## Khái quát

-Trong file PDF, chữ ký số (Digital Signature) không được lưu tách biệt mà được nhúng trực tiếp vào cấu trúc object của file PDF.
-PDF là một định dạng theo cấu trúc cây (object tree), trong đó mọi thành phần (trang, form, chữ ký, nội dung hiển thị…) đều là các object có ID và reference lẫn nhau.

## Các thành phần chính liên quan chữ ký

-Catalog (Root): Là đối tượng gốc của tài liệu PDF. Trỏ đến cấu trúc trang (/Pages) và biểu mẫu (/AcroForm).

-Pages Tree:

Quản lý toàn bộ danh sách các trang trong tài liệu. Mỗi trang là một Page object.

-Page Object

Đại diện cho từng trang (có nội dung, annotation, form fields).

-Resources

Tài nguyên đồ họa/text dùng trong trang (font, image, XObject…).

-Content Streams

Dòng lệnh vẽ nội dung hiển thị (text, hình ảnh). Không chứa chữ ký.

-XObject

Đối tượng mở rộng (ảnh, form con). Không trực tiếp chứa chữ ký, nhưng có thể được tham chiếu trong trang ký.

-AcroForm

Biểu mẫu PDF chứa danh sách các field (bao gồm field chữ ký). Đây là nơi quản lý các Signature field.

-Signature Field (Widget)

Trường hiển thị vùng chữ ký trong PDF. Thường có /T (tên field), /FT /Sig, /V trỏ đến dictionary chữ ký.

-Signature Dictionary (/Sig)

Thực thể chính chứa dữ liệu chữ ký số. Bao gồm:

• /Filter và /SubFilter: định nghĩa chuẩn chữ ký (như adbe.pkcs7.detached hoặc ETSI.CAdES.detached).

• /Contents: chứa nội dung chữ ký (chuỗi PKCS#7, dạng hex).

• /ByteRange: vùng byte được ký (tránh vòng lặp).

• /M: thời gian ký.

-/ByteRange

Mảng 4 giá trị xác định phạm vi byte của file được ký (phần /Contents bị bỏ qua khi tạo hash).

-/Contents

Dữ liệu chữ ký thật, thường là cấu trúc PKCS#7/CMS.

-Incremental Updates

Mỗi lần ký hoặc chỉnh sửa, PDF không ghi đè mà thêm phần mới vào cuối file (append-only). Nhờ vậy, ta có thể có nhiều chữ ký trong một file PDF.

-DSS (Document Security Store) (PAdES)

Lưu thông tin hỗ trợ xác thực lâu dài: chứng chỉ, OCSP, CRL, timestamp. Giúp đảm bảo chữ ký còn hợp lệ dù CA gốc hết hạn.

## Liệt kê & vai trò object refs quan trọng

<img width="562" height="676" alt="image" src="https://github.com/user-attachments/assets/908268cc-df53-4db6-a43c-5639c4b07451" />

## Sơ đồ cấu trúc (Object Tree)

Root (Catalog)
 ├── /Pages
 │     └── Page
 │          ├── /Resources
 │          ├── /Contents
 │          └── /Annots → [SignatureField]
 │
 └── /AcroForm
       └── /Fields → [SignatureField]
                    └── /V (Signature Dictionary)
                         ├── /Filter /SubFilter
                         ├── /ByteRange
                         ├── /Contents (PKCS#7)
                         ├── /M (timestamp)
                         └── /Reference /Cert /DSS
## Ghi chú thêm

PDF ký nhiều lần → Mỗi lần thêm một incremental update, không ghi đè, giúp truy vết lịch sử ký.

/ByteRange đảm bảo chỉ vùng được phép bị hash, tránh “self-reference”.

/Contents lưu ở dạng hex hoặc binary, có thể giải mã ra file .p7s bằng công cụ như openssl.

DSS chỉ có trong PDF chuẩn PAdES (Long-Term Validation).

# Thời gian ký được lưu ở đâu?

## Các vị trí có thể lưu thông tin thời gian

<img width="512" height="625" alt="image" src="https://github.com/user-attachments/assets/4a02da95-3e31-4c47-9c1c-91fd89d4fedc" />

## Giải thích khác biệt giữa /M và Timestamp RFC 3161

<img width="449" height="500" alt="image" src="https://github.com/user-attachments/assets/e6b34799-0317-4400-9023-b0549faf3db2" />

## Kết quả
<img width="613" height="783" alt="image" src="https://github.com/user-attachments/assets/9d696e09-4959-4546-a4bc-3132a1a3c492" />


