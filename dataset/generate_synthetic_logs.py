import json
import random
import uuid
import os
from datetime import datetime, timezone, timedelta

# ---------- CONFIGURAÇÕES ----------
NUM_LOGS = 1000          # quantidade total de logs a gerar
NOISE_PERCENTAGE = 0.1   # porcentagem de logs com ruído (duplicados ou irrelevantes)

SERVICES = [
    "orders-service",
    "payments-service",
    "inventory-service",
    "shipping-service",
    "customers-service"
]

LEVELS = ["INFO", "WARN", "ERROR"]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE"]

# Tags por tipo de operação
TAGS_BY_OPERATION = {
    "create": ["write", "create"],
    "read": ["read"],
    "update": ["write", "update"],
    "delete": ["write", "delete"],
    "timeout": ["timeout", "error"],
    "validation": ["validation", "error"],
}

# Mensagens e contextos por serviço
SCENARIOS = {
    "orders-service": [
        {
            "message": "Order {id} successfully created",
            "level": "INFO",
            "http_method": "POST",
            "http_path": "/orders",
            "status_code": 201,
            "tags": ["order", "write", "create"]
        },
        {
            "message": "Order validation failed for customer {customer_id}: missing payment method",
            "level": "ERROR",
            "http_method": "POST",
            "http_path": "/orders",
            "status_code": 400,
            "tags": ["order", "validation", "error"],
            "error_type": "ValidationException"
        },
        {
            "message": "Order {id} cancelled by user",
            "level": "WARN",
            "http_method": "DELETE",
            "http_path": "/orders/{id}",
            "status_code": 200,
            "tags": ["order", "delete", "user-action"]
        },
    ],
    "payments-service": [
        {
            "message": "Payment processed successfully for order {order_id}",
            "level": "INFO",
            "http_method": "POST",
            "http_path": "/payments",
            "status_code": 200,
            "tags": ["payment", "write", "success"]
        },
        {
            "message": "Insufficient funds for transaction {transaction_id}",
            "level": "ERROR",
            "http_method": "POST",
            "http_path": "/payments",
            "status_code": 402,
            "tags": ["payment", "error", "insufficient-funds"],
            "error_type": "PaymentDeclinedException"
        },
        {
            "message": "Payment gateway timeout for provider {provider}",
            "level": "ERROR",
            "http_method": "POST",
            "http_path": "/payments",
            "status_code": 504,
            "tags": ["payment", "timeout", "gateway"],
            "error_type": "TimeoutException"
        },
    ],
    "inventory-service": [
        {
            "message": "Stock level updated for product {product_id}: {quantity} units",
            "level": "INFO",
            "http_method": "PUT",
            "http_path": "/inventory/{product_id}",
            "status_code": 200,
            "tags": ["inventory", "update", "stock"]
        },
        {
            "message": "Stock level below threshold for product {product_id}",
            "level": "WARN",
            "http_method": "GET",
            "http_path": "/inventory/{product_id}",
            "status_code": 200,
            "tags": ["inventory", "read", "low-stock", "alert"]
        },
        {
            "message": "Inventory synchronization failed: database connection lost",
            "level": "ERROR",
            "http_method": "POST",
            "http_path": "/inventory/sync",
            "status_code": 503,
            "tags": ["inventory", "sync", "error", "database"],
            "error_type": "DatabaseConnectionException"
        },
    ],
    "shipping-service": [
        {
            "message": "Shipping label created for order {order_id}",
            "level": "INFO",
            "http_method": "POST",
            "http_path": "/shipping/labels",
            "status_code": 201,
            "tags": ["shipping", "create", "label"]
        },
        {
            "message": "Shipment delayed due to weather conditions in {region}",
            "level": "WARN",
            "http_method": "GET",
            "http_path": "/shipping/status/{tracking_id}",
            "status_code": 200,
            "tags": ["shipping", "delay", "weather"]
        },
        {
            "message": "Shipping address invalid for order {order_id}",
            "level": "ERROR",
            "http_method": "POST",
            "http_path": "/shipping/labels",
            "status_code": 400,
            "tags": ["shipping", "validation", "error", "address"],
            "error_type": "InvalidAddressException"
        },
    ],
    "customers-service": [
        {
            "message": "Customer profile {customer_id} updated successfully",
            "level": "INFO",
            "http_method": "PUT",
            "http_path": "/customers/{customer_id}",
            "status_code": 200,
            "tags": ["customer", "update", "profile"]
        },
        {
            "message": "Failed to fetch customer {customer_id}: timeout",
            "level": "ERROR",
            "http_method": "GET",
            "http_path": "/customers/{customer_id}",
            "status_code": 504,
            "tags": ["customer", "read", "timeout"],
            "error_type": "TimeoutException"
        },
        {
            "message": "Customer account created: {customer_id}",
            "level": "INFO",
            "http_method": "POST",
            "http_path": "/customers",
            "status_code": 201,
            "tags": ["customer", "create", "account"]
        },
    ]
}


def random_timestamp():
    """Gera um timestamp ISO 8601 recente."""
    now = datetime.now(timezone.utc)
    delta = timedelta(seconds=random.randint(-86400, 0))  # até 24h atrás
    return (now + delta).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def generate_log():
    """Gera um log sintético seguindo o formato definido em log_model.json."""
    service = random.choice(SERVICES)
    scenario = random.choice(SCENARIOS[service])

    # Gera IDs realistas
    order_id = random.randint(1, 9999)
    customer_id = random.randint(1, 999)
    product_id = random.randint(100, 999)
    transaction_id = f"txn-{uuid.uuid4().hex[:8]}"
    tracking_id = f"TRK{random.randint(100000, 999999)}"

    # Formata a mensagem com valores dinâmicos
    message = scenario["message"].format(
        id=order_id,
        order_id=order_id,
        customer_id=customer_id,
        product_id=product_id,
        transaction_id=transaction_id,
        tracking_id=tracking_id,
        quantity=random.randint(1, 100),
        provider=random.choice(["stripe", "paypal", "adyen"]),
        region=random.choice(["north", "south", "east", "west"])
    )

    # Constrói o log base
    log = {
        "timestamp": random_timestamp(),
        "level": scenario["level"],
        "service": service,
        "instance": f"pod-{random.randint(1000, 9999)}",
        "request_id": f"req-{uuid.uuid4().hex[:6]}",
        "trace_id": uuid.uuid4().hex[:12],
        "message": message,
        "http": {
            "method": scenario["http_method"],
            "path": scenario["http_path"].format(
                id=order_id,
                customer_id=customer_id,
                product_id=product_id,
                tracking_id=tracking_id
            ),
            "status_code": scenario["status_code"]
        },
        "tags": scenario["tags"]
    }

    # Adiciona erro se o cenário tiver um
    if "error_type" in scenario:
        log["error"] = {
            "type": scenario["error_type"],
            "message": message.split(": ")[-1] if ": " in message else "operation failed"
        }

    return log


def inject_noise(logs):
    """Insere ruído: logs duplicados, mensagens vazias, campos faltando."""
    noisy_logs = []
    for log in logs:
        if random.random() < NOISE_PERCENTAGE:
            noise_type = random.choice(["duplicate", "empty_message", "missing_fields"])
            if noise_type == "duplicate":
                noisy_logs.append(log.copy())  # duplica
            elif noise_type == "empty_message":
                log["message"] = ""
            elif noise_type == "missing_fields":
                # Remove campos opcionais
                log.pop("trace_id", None)
                log.pop("error", None)
                if "http" in log:
                    log.pop("http", None)
        noisy_logs.append(log)
    return noisy_logs


def main():
    logs = [generate_log() for _ in range(NUM_LOGS)]
    logs = inject_noise(logs)

    # Ordena por timestamp para simular ordem cronológica
    logs.sort(key=lambda x: x.get("timestamp", ""))

    # Define caminho absoluto para o arquivo na pasta dataset/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "synthetic_logs.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

    print(f"✅ Gerados {len(logs)} logs sintéticos em '{output_file}'")
    print(f"📊 Estatísticas:")
    print(f"   - INFO: {sum(1 for l in logs if l.get('level') == 'INFO')}")
    print(f"   - WARN: {sum(1 for l in logs if l.get('level') == 'WARN')}")
    print(f"   - ERROR: {sum(1 for l in logs if l.get('level') == 'ERROR')}")
    print(f"   - Com erros: {sum(1 for l in logs if 'error' in l)}")


if __name__ == "__main__":
    main()
