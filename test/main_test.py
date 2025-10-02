import requests
import os

def get_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    """
    获取 Microsoft Graph API access_token
    """
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }
    r = requests.post(url, data=data)
    if r.status_code != 200:
        raise Exception(f"获取 access_token 失败: {r.status_code} {r.text}")
    return r.json().get("access_token")


def word_to_pdf_ms_graph(input_path: str, output_path: str, access_token: str):
    """
    使用 Microsoft Graph API 将 Word 文件转换为 PDF 并保存。
    """
    filename = os.path.basename(input_path)

    # 上传 Word 文件到 OneDrive 根目录
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filename}:/content"
    with open(input_path, "rb") as f:
        response = requests.put(upload_url, headers={"Authorization": f"Bearer {access_token}"}, data=f)

    if response.status_code not in (200, 201):
        raise Exception(f"上传文件失败: {response.status_code} {response.text}")

    file_id = response.json()["id"]

    # 下载 PDF
    download_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content?format=pdf"
    pdf_response = requests.get(download_url, headers={"Authorization": f"Bearer {access_token}"})

    if pdf_response.status_code != 200:
        raise Exception(f"转换 PDF 失败: {pdf_response.status_code} {pdf_response.text}")

    with open(output_path, "wb") as f:
        f.write(pdf_response.content)

    print(f"✅ PDF 已保存到: {output_path}")


if __name__ == "__main__":
    # 替换成你自己的 Azure 应用信息
    tenant_id = "YOUR_TENANT_ID"
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"

    # 输入和输出文件
    word_file = "example.docx"   # 需要转换的 Word 文件
    pdf_file = "example.pdf"     # 输出的 PDF 文件

    # 获取 Token
    token = get_access_token(tenant_id, client_id, client_secret)

    # Word 转 PDF
    word_to_pdf_ms_graph(word_file, pdf_file, token)
