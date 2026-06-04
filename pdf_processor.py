import pikepdf
from dataclasses import dataclass


@dataclass
class PDFInfo:
    path: str
    is_encrypted: bool
    has_owner_password: bool
    has_user_password: bool
    permissions: dict


PERMISSION_BITS = {
    0x04: "允许低分辨率打印",
    0x08: "允许修改",
    0x10: "允许复制",
    0x20: "允许注释",
    0x100: "允许填写表单",
    0x200: "允许提取",
    0x400: "允许组装",
    0x800: "允许高分辨率打印",
    0x1000: "允许无障碍访问",
}


def check_restrictions(pdf_path: str, password: str = "") -> PDFInfo:
    try:
        pdf = pikepdf.open(pdf_path, password=password)
    except pikepdf.PasswordError:
        raise ValueError("密码错误或文件需要密码")
    except pikepdf.PdfError as e:
        raise ValueError(f"无法打开PDF文件: {e}")

    is_encrypted = pdf.is_encrypted
    has_user_password = False
    has_owner_password = False
    permissions = {}

    if is_encrypted:
        enc = pdf.encryption
        if enc:
            has_user_password = bool(enc.user_password)
            P = enc.P
            for bit, label in PERMISSION_BITS.items():
                permissions[label] = bool(P & bit)
    else:
        for _, label in PERMISSION_BITS.items():
            permissions[label] = True

    pdf.close()

    return PDFInfo(
        path=pdf_path,
        is_encrypted=is_encrypted,
        has_owner_password=has_owner_password,
        has_user_password=has_user_password,
        permissions=permissions,
    )


def remove_restrictions(input_path: str, output_path: str, password: str = "") -> bool:
    try:
        pdf = pikepdf.open(input_path, password=password)
    except pikepdf.PasswordError:
        raise ValueError("密码错误或文件需要密码")
    except pikepdf.PdfError as e:
        raise ValueError(f"无法打开PDF文件: {e}")

    pdf.save(output_path)
    pdf.close()
    return True
