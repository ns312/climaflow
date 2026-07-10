import os
from playwright.sync_api import sync_playwright

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Коммерческое предложение для отелей ClimaFlow</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3, .font-montserrat {
            font-family: 'Montserrat', sans-serif;
        }
        .page-break {
            page-break-before: always;
        }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased print:bg-white">

    <!-- PAGE 1 -->
    <div class="w-[210mm] min-h-[297mm] p-12 mx-auto bg-white shadow-xl relative overflow-hidden flex flex-col justify-between print:shadow-none print:p-8">
        <!-- Top Tech Gradient Bar -->
        <div class="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-blue-600 to-cyan-500"></div>

        <div>
            <!-- Header -->
            <div class="flex justify-between items-center border-b pb-6 border-slate-100">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white font-extrabold text-xl shadow-lg shadow-blue-500/20">CF</div>
                    <div>
                        <span class="text-xl font-bold tracking-tight text-slate-900">Clima<span class="text-blue-600">Flow</span></span>
                        <span class="block text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Климатический Сервис</span>
                    </div>
                </div>
                <div class="text-right">
                    <a href="tel:+996502985896" class="text-sm font-bold text-slate-900 block hover:text-blue-600 transition-colors">+996 (502) 98-58-96</a>
                    <a href="https://wa.me/996502985896?text=Хочу%20диагностику%20отеля" class="text-xs text-blue-600 font-medium underline">Связаться в WhatsApp</a>
                </div>
            </div>

            <!-- Title & Subtitle -->
            <div class="mt-12 text-center">
                <span class="px-4 py-1.5 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold uppercase tracking-wider inline-block">Эксклюзивное предложение для отелей, гостевых домов и хостелов</span>
                <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight leading-tight mt-4 max-w-2xl mx-auto">
                    Как отелям Бишкека сэкономить на электричестве и защитить рейтинг на <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">Booking.com</span> от плохих отзывов?
                </h1>
                <p class="text-slate-600 mt-4 max-w-xl mx-auto text-sm leading-relaxed">
                    Для гостиничного бизнеса комфорт гостей в номерах — основа репутации. Всего один негативный отзыв о неработающем или шумящем кондиционере снижает рейтинг отеля и отпугивает сотни будущих клиентов.
                </p>
            </div>

            <!-- 3 Main Pain Points / Threats for Hotels -->
            <div class="grid grid-cols-3 gap-6 mt-12">
                <div class="p-6 rounded-2xl bg-slate-50 border border-slate-100 flex flex-col justify-between">
                    <div>
                        <div class="w-10 h-10 rounded-lg bg-red-50 text-red-600 flex items-center justify-center mb-4">
                            <!-- Star/Review Icon -->
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499c.15-.363.68-.363.83 0l2.399 4.863 5.347.777c.4.058.56.558.27.852l-3.87 3.77 1.053 5.295c.08.4-.34.707-.7.502l-4.793-2.52-4.793 2.52c-.36.205-.78-.102-.7-.502l1.053-5.295-3.87-3.77c-.29-.294-.13-.794.27-.852l5.347-.777 2.399-4.863Z" />
                            </svg>
                        </div>
                        <h3 class="font-bold text-slate-900 text-sm">Угроза №1: Слив рейтинга</h3>
                        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
                            Духота в номере или гул от внешнего блока ночью гарантируют 1 звезду на Booking.com и 2ГИС. Низкий рейтинг напрямую уменьшает загрузку отеля на 30-40%.
                        </p>
                    </div>
                </div>

                <div class="p-6 rounded-2xl bg-slate-50 border border-slate-100 flex flex-col justify-between">
                    <div>
                        <div class="w-10 h-10 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center mb-4">
                            <!-- Bolt/Energy Icon -->
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                                <path stroke-linecap="round" stroke-linejoin="round" d="m3.75 13.5 10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75Z" />
                            </svg>
                        </div>
                        <h3 class="font-bold text-slate-900 text-sm">Угроза №2: Огромные счета за свет</h3>
                        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
                            Забитые пылью фильтры заставляют компрессор работать на максимуме. Энергопотребление кондиционеров вырастает на **30-50%**, раздувая ваши счета за электричество.
                        </p>
                    </div>
                </div>

                <div class="p-6 rounded-2xl bg-slate-50 border border-slate-100 flex flex-col justify-between">
                    <div>
                        <div class="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
                            <!-- Biohazard/Mold Icon -->
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0Z" />
                            </svg>
                        </div>
                        <h3 class="font-bold text-slate-900 text-sm">Угроза №3: Запах сырости и аллергия</h3>
                        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
                            Конденсат во внутреннем блоке — идеальная среда для плесени и легионелл. Грибковый запах сырости в номере вызывает жалобы гостей на аллергию и головную боль.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Value Prop Banner -->
            <div class="mt-10 p-6 rounded-2xl bg-blue-600 text-white flex items-center justify-between">
                <div class="max-w-[70%]">
                    <h3 class="font-bold text-base">Чистая техника экономит электроэнергию и исключает поломки!</h3>
                    <p class="text-[11px] text-blue-100 mt-1 leading-relaxed">
                        Регулярное ТО снижает нагрузку на сеть, снижает счета за электроэнергию отеля до 30% и защищает ваши компрессоры от дорогостоящего выгорания.
                    </p>
                </div>
                <div class="text-right">
                    <span class="text-xs uppercase tracking-widest text-blue-200 block font-semibold">Снижение счетов за свет</span>
                    <span class="text-3xl font-extrabold">до 30%</span>
                </div>
            </div>
        </div>

        <!-- Page 1 Footer -->
        <div class="flex justify-between items-center text-xs text-slate-400 border-t pt-4 border-slate-100 mt-auto">
            <span>Коммерческое предложение для отелей | ClimaFlow</span>
            <span class="font-semibold text-slate-500">Страница 1 из 2</span>
        </div>
    </div>

    <!-- PAGE 2 -->
    <div class="page-break w-[210mm] min-h-[297mm] p-12 mx-auto bg-white shadow-xl relative overflow-hidden flex flex-col justify-between print:shadow-none print:p-8">
        <!-- Top Tech Gradient Bar -->
        <div class="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-blue-600 to-cyan-500"></div>

        <div>
            <!-- Header (Short) -->
            <div class="flex justify-between items-center border-b pb-6 border-slate-100">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white font-extrabold text-sm">CF</div>
                    <span class="text-lg font-bold text-slate-900">ClimaFlow</span>
                </div>
                <span class="text-xs text-slate-400">Специальный тариф</span>
            </div>

            <!-- Financial Comparison Table -->
            <div class="mt-10">
                <h2 class="text-xl font-bold text-slate-900 tracking-tight">Экономика отеля: обслуживание против форс-мажора</h2>
                <p class="text-xs text-slate-500 mt-1">Регулярный сервис окупается при первом же предотвращении простоя номера:</p>
                
                <table class="w-full mt-6 text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 border-b border-slate-100">
                            <th class="p-3 text-xs font-bold uppercase text-slate-600 tracking-wider">Тип услуги</th>
                            <th class="p-3 text-xs font-bold uppercase text-slate-600 tracking-wider">Цена для отелей</th>
                            <th class="p-3 text-xs font-bold uppercase text-slate-600 tracking-wider">Результат для отеля</th>
                        </tr>
                    </thead>
                    <tbody class="text-xs divide-y divide-slate-100">
                        <tr>
                            <td class="p-3 font-semibold text-slate-900">Комплексный сервис ClimaFlow (Отель)</td>
                            <td class="p-3 text-blue-600 font-bold">от 1 200 сом</td>
                            <td class="p-3 text-slate-500">Дезинфекция внутреннего блока, чистка внешнего блока от тополиного пуха и пыли, замер давления, заправка. Тихая работа прибора.</td>
                        </tr>
                        <tr>
                            <td class="p-3 font-semibold text-slate-900">Замена компрессора (внешний блок)</td>
                            <td class="p-3 text-red-600 font-bold">от 25 000 сом</td>
                            <td class="p-3 text-slate-500">Экстренный ремонт, перенос броней гостей, простой номера и упущенная прибыль.</td>
                        </tr>
                        <tr>
                            <td class="p-3 font-semibold text-slate-900">Простой 1 номера (сезон)</td>
                            <td class="p-3 text-red-700 font-bold">от 4 000 сом / сутки</td>
                            <td class="p-3 text-slate-500">Прямые убытки гостиницы из-за невозможности заселить гостей в жаркий номер.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Our Zero-Risk Offer -->
            <div class="mt-10 p-8 rounded-2xl bg-slate-50 border border-blue-100 relative overflow-hidden">
                <div class="absolute -right-16 -top-16 w-36 h-36 rounded-full bg-blue-100/30 -z-0"></div>
                <div class="relative z-10">
                    <span class="text-[10px] font-bold uppercase tracking-widest text-blue-600 bg-blue-50 px-3 py-1 rounded-full">Бесплатный тест</span>
                    <h2 class="text-2xl font-extrabold text-slate-900 mt-3">Тест-драйв: Бесплатная диагностика 3 номеров</h2>
                    <p class="text-xs text-slate-600 mt-2 leading-relaxed">
                        Мы бесплатно приедем в ваш отель и проведем детальный аудит кондиционеров в **первых 3 номерах** (или в лобби/ресепшене). Вы оцените уровень нашего сервиса и получите детальный отчет о состоянии климата.
                    </p>
                    
                    <div class="grid grid-cols-2 gap-4 mt-6">
                        <div class="flex items-start gap-2">
                            <span class="text-blue-600 font-bold text-sm">✓</span>
                            <span class="text-xs text-slate-600 font-medium">Замер уровня хладагента (давления фреона)</span>
                        </div>
                        <div class="flex items-start gap-2">
                            <span class="text-blue-600 font-bold text-sm">✓</span>
                            <span class="text-xs text-slate-600 font-medium">Анализ уровня шума и вибрации сплит-систем</span>
                        </div>
                        <div class="flex items-start gap-2">
                            <span class="text-blue-600 font-bold text-sm">✓</span>
                            <span class="text-xs text-slate-600 font-medium">Проверка дренажа (чтобы не затопить обои)</span>
                        </div>
                        <div class="flex items-start gap-2">
                            <span class="text-blue-600 font-bold text-sm">✓</span>
                            <span class="text-xs text-slate-600 font-medium">Оценка эффективности охлаждения комнат</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Call to Action Section -->
            <div class="mt-12 text-center">
                <h3 class="font-bold text-slate-900 text-sm">Хотите защитить оценки вашего отеля на Booking.com?</h3>
                <p class="text-xs text-slate-500 mt-1">Забронируйте визит инженера для бесплатного тест-драйва прямо сейчас</p>
                
                <div class="mt-6 flex flex-col items-center gap-4">
                    <!-- CTA Button -->
                    <a href="https://wa.me/996502985896?text=Хочу%20бесплатную%20диагностику%20номеров%20отеля" class="px-8 py-3.5 rounded-xl bg-blue-600 text-white font-bold text-xs uppercase tracking-wider hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/20 inline-block font-montserrat">
                        Записаться на бесплатный тест-драйв (0 сом)
                    </a>
                    
                    <div class="flex items-center gap-6 mt-2 text-xs">
                        <div>
                            <span class="text-slate-400">Наш сайт:</span>
                            <a href="https://climaflow312.kg" class="font-bold text-slate-900 underline block hover:text-blue-600 transition-colors">climaflow312.kg</a>
                        </div>
                        <div class="w-px h-6 bg-slate-200"></div>
                        <div>
                            <span class="text-slate-400">Телефон (Руслан):</span>
                            <a href="tel:+996502985896" class="font-bold text-slate-900 underline block hover:text-blue-600 transition-colors">+996 (502) 98-58-96</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Page 2 Footer -->
        <div class="flex justify-between items-center text-xs text-slate-400 border-t pt-4 border-slate-100 mt-auto">
            <span>Коммерческое предложение для отелей | ClimaFlow</span>
            <span class="font-semibold text-slate-500">Страница 2 из 2</span>
        </div>
    </div>

</body>
</html>
"""

def generate_pdf():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    html_path = os.path.join(script_dir, "kp_hotels.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"Временный HTML-файл записан в {html_path}")
    
    pdf_path = os.path.join(script_dir, "kp_hotels_climaflow.pdf")
    
    with sync_playwright() as p:
        print("Запуск браузера для генерации PDF...")
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context()
        page = context.new_page()
        
        page.goto(f"file://{html_path}")
        
        print("Ожидание завершения загрузки ресурсов...")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000) 
        
        print("Экспорт в PDF...")
        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
        )
        
        browser.close()
    
    if os.path.exists(html_path):
        os.remove(html_path)
        
    print(f"Успешно сгенерирован PDF-файл: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
