import requests


def send_to_n8n(phone: str, account: str, hotWater: str, coldWater: str):
    url = "https://kirill-syudi2.app.n8n.cloud/webhook-test/insert-record"

    payload = {
        "phone": phone,
        "account": account,
        "hotWater": hotWater,
        "coldWater": coldWater
    }

    response = requests.post(url, json=payload, timeout=10)
    return response.status_code, response.text


# пример вызова
if __name__ == "__main__":
    status, text = send_to_n8n(
        phone="1234567890",
        account="9876543210",
        hotWater="12345",
        coldWater="67890"
    )
    print(status, text)