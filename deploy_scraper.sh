#!/bin/bash
# =====================================================================
# Скрипт развертывания Парсера и Telegram-Управления на сервере Google
# =====================================================================

cd ~/climaflow

echo "=== Шаг 1. Запуск Telegram-Управления в фоне ==="
pkill -f telegram_controller.py
nohup ./venv/bin/python -u telegram_controller.py > telegram.log 2>&1 &

echo "=== РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО ==="
