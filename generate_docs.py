import os
import re
from playwright.sync_api import sync_playwright

# HTML для Счета на оплату с НДС 12% и НСП
INVOICE_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Счет на оплату № 45</title>
    <style>
        body {
            font-family: "Arial", sans-serif;
            font-size: 11px;
            line-height: 1.4;
            color: #000;
            margin: 0;
            padding: 20px;
        }
        .bank-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .bank-table td {
            border: 1px solid #000;
            padding: 5px;
            vertical-align: top;
        }
        .bank-header {
            font-size: 10px;
            color: #333;
            margin-bottom: 2px;
        }
        .title {
            font-size: 16px;
            font-weight: bold;
            border-bottom: 2px solid #000;
            padding-bottom: 8px;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        .details-table {
            width: 100%;
            margin-bottom: 20px;
            font-size: 11px;
        }
        .details-table td {
            padding: 3px 0;
            vertical-align: top;
        }
        .details-label {
            width: 90px;
            font-weight: bold;
        }
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        .items-table th {
            border: 1px solid #000;
            background-color: #f2f2f2;
            padding: 6px 3px;
            font-weight: bold;
            text-align: center;
            font-size: 10px;
        }
        .items-table td {
            border: 1px solid #000;
            padding: 6px 4px;
            vertical-align: middle;
        }
        .text-center { text-align: center; }
        .text-right { text-align: right; }
        .totals-table {
            width: 45%;
            margin-left: auto;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .totals-table td {
            padding: 3px;
        }
        .total-row {
            font-weight: bold;
            font-size: 12px;
        }
        .words-total {
            font-weight: bold;
            margin-bottom: 25px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 10px;
        }
        .signatures {
            width: 100%;
            margin-top: 35px;
            border-collapse: collapse;
        }
        .signatures td {
            padding: 8px 0;
        }
        .sig-line {
            border-bottom: 1px solid #000;
            width: 150px;
            display: inline-block;
        }
    </style>
</head>
<body>

    <!-- Банковские реквизиты получателя -->
    <table class="bank-table">
        <tr>
            <td colspan="2" rowspan="2" style="width: 50%;">
                <div class="bank-header">Получатель</div>
                <strong>ИП Сыдыков Нурсултан Бакытбекович</strong>
            </td>
            <td style="width: 20%;">
                <div class="bank-header">ИНН</div>
                20308199301488
            </td>
            <td style="width: 30%;">
                <div class="bank-header">Р/счет №</div>
                1033020010229609
            </td>
        </tr>
        <tr>
            <td>
                <div class="bank-header">БИК</div>
                103030
            </td>
            <td>
                <div class="bank-header">Код ОКПО</div>
                —
            </td>
        </tr>
        <tr>
            <td colspan="2">
                <div class="bank-header">Банк получателя</div>
                ФИЛИАЛ "МБАНК АЗИЯ MOL" ОАО "МБАНК", БИШКЕК
            </td>
            <td>
                <div class="bank-header">ГНИ код</div>
                —
            </td>
            <td>
                &nbsp;
            </td>
        </tr>
    </table>

    <div class="title">Счет на оплату № 45 от 09 июля 2026 г.</div>

    <!-- Реквизиты сторон -->
    <table class="details-table">
        <tr>
            <td class="details-label">Поставщик:</td>
            <td><strong>ИП Сыдыков Нурсултан Бакытбекович</strong>, ИНН: 20308199301488, Расчетный счет: 1033020010229609 в ФИЛИАЛ "МБАНК АЗИЯ МОЛЛ" ОАО "МБАНК", БИК: 103030</td>
        </tr>
        <tr style="height: 5px;"><td></td><td></td></tr>
        <tr>
            <td class="details-label">Покупатель:</td>
            <td><strong>ЗАО "Акун"</strong>, ИНН: 01103199710085, ОКПО: 21678574, Адрес: г. Бишкек, пр. Ден Сяопина 308, Расчетный счет: 1240020001727212 в ОАО "БАКАЙ БАНК", БИК: 124030</td>
        </tr>
    </table>

    <!-- Таблица товаров/услуг с НДС и НСП -->
    <table class="items-table">
        <thead>
            <tr>
                <th style="width: 4%;">№</th>
                <th style="width: 38%;">Наименование товара, работ, услуг</th>
                <th style="width: 5%;">Кол.</th>
                <th style="width: 5%;">Ед.</th>
                <th style="width: 14%;">Цена без налогов (сом)</th>
                <th style="width: 11%;">НДС 12% (сом)</th>
                <th style="width: 10%;">НСП (сом)</th>
                <th style="width: 13%;">Всего (сом)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="text-center">1</td>
                <td>Кондиционер BALLU 12 BSAGI iGreen Pro INVERTER(R32) (до 40м2, зима-лето, Invertor)</td>
                <td class="text-center">1</td>
                <td class="text-center">шт.</td>
                <td class="text-right">29 480,00</td>
                <td class="text-right">3 537,60</td>
                <td class="text-right">294,80 <span style="font-size:9px;color:#666;">(1%)</span></td>
                <td class="text-right">33 312,40</td>
            </tr>
            <tr>
                <td class="text-center">2</td>
                <td>Установка кондиционера (монтаж)</td>
                <td class="text-center">1</td>
                <td class="text-center">услуга</td>
                <td class="text-right">5 800,00</td>
                <td class="text-right">696,00</td>
                <td class="text-right">116,00 <span style="font-size:9px;color:#666;">(2%)</span></td>
                <td class="text-right">6 612,00</td>
            </tr>
            <tr>
                <td class="text-center">3</td>
                <td>Расходные материалы (кронштейн, чопики)</td>
                <td class="text-center">1</td>
                <td class="text-center">компл.</td>
                <td class="text-right">750,00</td>
                <td class="text-right">90,00</td>
                <td class="text-right">7,50 <span style="font-size:9px;color:#666;">(1%)</span></td>
                <td class="text-right">847,50</td>
            </tr>
            <tr>
                <td class="text-center">4</td>
                <td>Доставка кондиционера</td>
                <td class="text-center">1</td>
                <td class="text-center">услуга</td>
                <td class="text-right">0,00</td>
                <td class="text-right">0,00</td>
                <td class="text-right">0,00 <span style="font-size:9px;color:#666;">(0%)</span></td>
                <td class="text-right">0,00</td>
            </tr>
        </tbody>
    </table>

    <!-- Итоги -->
    <table class="totals-table">
        <tr>
            <td class="text-right">Сумма без налогов:</td>
            <td class="text-right" style="width: 110px;">36 030,00</td>
        </tr>
        <tr>
            <td class="text-right">НДС 12%:</td>
            <td class="text-right">4 323,60</td>
        </tr>
        <tr>
            <td class="text-right">НСП 1% (товары):</td>
            <td class="text-right">302,30</td>
        </tr>
        <tr>
            <td class="text-right">НСП 2% (услуги):</td>
            <td class="text-right">116,00</td>
        </tr>
        <tr class="total-row">
            <td class="text-right">Всего к оплате:</td>
            <td class="text-right">40 771,90</td>
        </tr>
    </table>

    <div class="words-total">
        Всего наименований 4, на сумму 40 771,90 сом.<br>
        <span style="font-weight: normal; font-style: italic;">Разписью: Сорок тысяч семьсот семьдесят один сом 90 тыйын.</span>
    </div>

    <!-- Подписи -->
    <table class="signatures">
        <tr>
            <td style="width: 15%;">Руководитель</td>
            <td style="width: 35%;"><span class="sig-line"></span> (Сыдыков Н. Б.)</td>
            <td style="width: 15%;">Бухгалтер</td>
            <td style="width: 35%;"><span class="sig-line"></span> (Сыдыков Н. Б.)</td>
        </tr>
    </table>

    <div style="margin-top: 40px; font-size: 9px; color: #555; text-align: center;">
        М.П. (При наличии печати)
    </div>

</body>
</html>
"""

# HTML для Акта выполненных работ с НДС 12% и НСП
ACT_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Акт выполненных работ № 45</title>
    <style>
        body {
            font-family: "Arial", sans-serif;
            font-size: 11px;
            line-height: 1.4;
            color: #000;
            margin: 0;
            padding: 20px;
        }
        .title {
            font-size: 15px;
            font-weight: bold;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .details-table {
            width: 100%;
            margin-bottom: 20px;
            font-size: 11px;
        }
        .details-table td {
            padding: 3px 0;
            vertical-align: top;
        }
        .details-label {
            width: 90px;
            font-weight: bold;
        }
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        .items-table th {
            border: 1px solid #000;
            background-color: #f2f2f2;
            padding: 6px 3px;
            font-weight: bold;
            text-align: center;
            font-size: 10px;
        }
        .items-table td {
            border: 1px solid #000;
            padding: 6px 4px;
            vertical-align: middle;
        }
        .text-center { text-align: center; }
        .text-right { text-align: right; }
        .totals-table {
            width: 45%;
            margin-left: auto;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .totals-table td {
            padding: 3px;
        }
        .total-row {
            font-weight: bold;
            font-size: 12px;
        }
        .statement {
            margin-top: 15px;
            margin-bottom: 25px;
            line-height: 1.5;
        }
        .signatures-container {
            width: 100%;
            margin-top: 35px;
            border-collapse: collapse;
        }
        .signatures-container td {
            width: 50%;
            vertical-align: top;
        }
        .sig-block {
            margin-top: 10px;
        }
        .sig-line {
            border-bottom: 1px solid #000;
            width: 150px;
            display: inline-block;
            margin-top: 8px;
        }
    </style>
</head>
<body>

    <div class="title">Акт выполненных работ (оказанных услуг) № 45<br>от 09 июля 2026 г.</div>

    <!-- Реквизиты сторон -->
    <table class="details-table">
        <tr>
            <td class="details-label">Исполнитель:</td>
            <td><strong>ИП Сыдыков Нурсултан Бакытбекович</strong>, ИНН: 20308199301488, Адрес: Бишкек, Расчетный счет: 1033020010229609 в ФИЛИАЛ "МБАНК АЗИЯ МОЛЛ" ОАО "МБАНК", БИК: 103030</td>
        </tr>
        <tr style="height: 5px;"><td></td><td></td></tr>
        <tr>
            <td class="details-label">Заказчик:</td>
            <td><strong>ЗАО "Акун"</strong>, ИНН: 01103199710085, ОКПО: 21678574, Адрес: г. Бишкек, пр. Ден Сяопина 308, Расчетный счет: 1240020001727212 в ОАО "БАКАЙ БАНК", БИК: 124030</td>
        </tr>
    </table>

    <!-- Таблица -->
    <table class="items-table">
        <thead>
            <tr>
                <th style="width: 4%;">№</th>
                <th style="width: 38%;">Наименование выполненных работ, оказанных услуг</th>
                <th style="width: 5%;">Кол.</th>
                <th style="width: 5%;">Ед.</th>
                <th style="width: 14%;">Цена без налогов (сом)</th>
                <th style="width: 11%;">НДС 12% (сом)</th>
                <th style="width: 10%;">НСП (сом)</th>
                <th style="width: 13%;">Всего (сом)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="text-center">1</td>
                <td>Поставка кондиционера BALLU 12 BSAGI iGreen Pro INVERTER(R32) (до 40м2, зима-лето, Invertor)</td>
                <td class="text-center">1</td>
                <td class="text-center">шт.</td>
                <td class="text-right">29 480,00</td>
                <td class="text-right">3 537,60</td>
                <td class="text-right">294,80 <span style="font-size:9px;color:#666;">(1%)</span></td>
                <td class="text-right">33 312,40</td>
            </tr>
            <tr>
                <td class="text-center">2</td>
                <td>Установка кондиционера (монтаж)</td>
                <td class="text-center">1</td>
                <td class="text-center">услуга</td>
                <td class="text-right">5 800,00</td>
                <td class="text-right">696,00</td>
                <td class="text-right">116,00 <span style="font-size:9px;color:#666;">(2%)</span></td>
                <td class="text-right">6 612,00</td>
            </tr>
            <tr>
                <td class="text-center">3</td>
                <td>Расходные материалы (кронштейн, чопики)</td>
                <td class="text-center">1</td>
                <td class="text-center">компл.</td>
                <td class="text-right">750,00</td>
                <td class="text-right">90,00</td>
                <td class="text-right">7,50 <span style="font-size:9px;color:#666;">(1%)</span></td>
                <td class="text-right">847,50</td>
            </tr>
            <tr>
                <td class="text-center">4</td>
                <td>Доставка кондиционера</td>
                <td class="text-center">1</td>
                <td class="text-center">услуга</td>
                <td class="text-right">0,00</td>
                <td class="text-right">0,00</td>
                <td class="text-right">0,00 <span style="font-size:9px;color:#666;">(0%)</span></td>
                <td class="text-right">0,00</td>
            </tr>
        </tbody>
    </table>

    <!-- Итоги -->
    <table class="totals-table">
        <tr>
            <td class="text-right">Сумма без налогов:</td>
            <td class="text-right" style="width: 110px;">36 030,00</td>
        </tr>
        <tr>
            <td class="text-right">НДС 12%:</td>
            <td class="text-right">4 323,60</td>
        </tr>
        <tr>
            <td class="text-right">НСП 1% (товары):</td>
            <td class="text-right">302,30</td>
        </tr>
        <tr>
            <td class="text-right">НСП 2% (услуги):</td>
            <td class="text-right">116,00</td>
        </tr>
        <tr class="total-row">
            <td class="text-right">Всего к оплате:</td>
            <td class="text-right">40 771,90</td>
        </tr>
    </table>

    <div class="statement">
        Вышеперечисленные работы (услуги) выполнены полностью и в срок. Заказчик претензий по объему, качеству и срокам оказания услуг не имеет.<br>
        Всего оказано услуг и поставлено товаров на сумму: <strong>40 771,90 сом (Сорок тысяч семьсот семьдесят один сом 90 тыйын)</strong>.
    </div>

    <!-- Подписи сторон -->
    <table class="signatures-container">
        <tr>
            <td>
                <strong>Исполнитель:</strong><br>
                ИП Сыдыков Нурсултан Бакытбекович
                <div class="sig-block">
                    Подпись: <span class="sig-line"></span><br>
                    М.П. (При наличии печати)
                </div>
            </td>
            <td>
                <strong>Заказчик:</strong><br>
                ЗАО "Акун"
                <div class="sig-block">
                    Подпись: <span class="sig-line"></span><br>
                    М.П. (При наличии печати)
                </div>
            </td>
        </tr>
    </table>

</body>
</html>
"""

def generate_documents():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Счёт
    invoice_html_path = os.path.join(script_dir, "invoice.html")
    with open(invoice_html_path, "w", encoding="utf-8") as f:
        f.write(INVOICE_HTML)
        
    # 2. Акт
    act_html_path = os.path.join(script_dir, "act.html")
    with open(act_html_path, "w", encoding="utf-8") as f:
        f.write(ACT_HTML)
        
    invoice_pdf_path = os.path.join(script_dir, "invoice_sydykov.pdf")
    act_pdf_path = os.path.join(script_dir, "act_sydykov.pdf")
    
    with sync_playwright() as p:
        print("Запуск браузера для генерации документов с НДС...")
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context()
        page = context.new_page()
        
        # Счёт в PDF
        print("Рендеринг Счёта в PDF...")
        page.goto(f"file://{invoice_html_path}")
        page.wait_for_load_state("networkidle")
        page.pdf(
            path=invoice_pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "15mm", "right": "15mm", "bottom": "15mm", "left": "15mm"}
        )
        
        # Акт в PDF
        print("Рендеринг Акта в PDF...")
        page.goto(f"file://{act_html_path}")
        page.wait_for_load_state("networkidle")
        page.pdf(
            path=act_pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "15mm", "right": "15mm", "bottom": "15mm", "left": "15mm"}
        )
        
        browser.close()
        
    # Удаляем временные HTML
    if os.path.exists(invoice_html_path):
        os.remove(invoice_html_path)
    if os.path.exists(act_html_path):
        os.remove(act_html_path)
        
    print("Документы с НДС успешно сгенерированы!")

if __name__ == "__main__":
    generate_documents()
