# Безопасность

## Чеклист

| Область | Мера | Статус |
|--------|------|--------|
| Данные в покое | Шифрование face_embedding AES-256-GCM | ✅ |
| Локальная БД | Шифрование SQLite (SQLCipher) | ✅ |
| Транспорт | TLS 1.3 | 🔲 |
| API-аутентификация | API-key в заголовке | ✅ |
| Пароль администратора | Хэширование bcrypt | 🔲 |
| Ключи шифрования | В .env | ✅ |
| Подделка лица | Liveness detection | 🔲 |
| Логи | Ротация, без PII | ✅ |

## Генерация ключей

```bash
# Ключ шифрования (256 бит)
python -c "import secrets; print(secrets.token_hex(32))"

# API-ключ
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Пароль администратора (bcrypt)
python -c "import bcrypt; print(bcrypt.hashpw(b'password', bcrypt.gensalt()).decode())"
```

## TLS

Настроить nginx с Let's Encrypt.