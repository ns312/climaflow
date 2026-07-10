import os
from playwright.sync_api import sync_playwright

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Коммерческое предложение ClimaFlow</title>
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
                    <!-- ClimaFlow Tech Logo -->
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white font-extrabold text-xl shadow-lg shadow-blue-500/20">CF</div>
                    <div>
                        <span class="text-xl font-bold tracking-tight text-slate-900">Clima<span class="text-blue-600">Flow</span></span>
                        <span class="block text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Климатический Сервис</span>
                    </div>
                </div>
                <div class="text-right">
                    <a href="tel:+996502985896" class="text-sm font-bold text-slate-900 block hover:text-blue-600 transition-colors">+996 (502) 98-58-96</a>
                    <a href="https://wa.me/996502985896?text=Хочу%20диагностику" class="text-xs text-blue-600 font-medium underline">Связаться в WhatsApp</a>
                </div>
            </div>

            <!-- Title & Subtitle -->
            <div class="mt-12 text-center">
                <span class="px-4 py-1.5 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold uppercase tracking-wider inline-block">Специальное предложение для ресторанов и кафе</span>
                <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight leading-tight mt-4 max-w-2xl mx-auto">
                    Как сэкономить до <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">70% на ремонте</span> кондиционеров и защитить ресторан в жару?
                </h1>
                <p class="text-slate-600 mt-4 max-w-xl mx-auto text-sm leading-relaxed">
                    Для ресторанного бизнеса исправный кондиционер — это не просто комфорт, а ключевой фактор выручки. Один день простоя в жару может стоить сотен тысяч сомов упущенной прибыли.
                </p>
            </div>

            <!-- 3 Main Pain Points / Threats -->
            <div class="grid grid-cols-3 gap-6 mt-12">
                <div class="p-6 rounded-2xl bg-slate-50 border border-slate-100 flex flex-col justify-between">
                    <div>
                        <div class="w-10 h-10 rounded-lg bg-red-50 text-red-600 flex items-center justify-center mb-4">
                            <!-- Hot Temp Icon -->
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v18m9-9H3" />
                            </svg>
                        </div>
                        <h3 class="font-bold text-slate-900 text-sm">Угроза №1: Потеря гостей</h3>
                        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
                            При поломке кондиционера температура в зале поднимается выше 30°C. Гости уходят к конкурентам, средний чек падает, репутация заведения страдает.
                        </p>
                    </div>
                </div>

                <div class="p-6 rounded-2xl bg-slate-50 border border-slate-100 flex flex-col justify-between">
                    <div>
                        <div class="w-10 h-10 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center mb-4">
                            <!-- Fire/Danger Icon -->
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M15.362 5.214A8.252 8.252 0 0 1 12 21 8.25 8.25 0 0 1 6.038 7.047 8.287 8.287 0 0 0 9 9.601a8.983 8.983 0 0 1 3.361-6.867 8.21 8.21 0 0 0 3 2.48Z" />
                            </svg>
                        </div>
                        <h3 class="font-bold text-slate-900 text-sm">Угроза №2: Жир и запах на кухне</h3>
                        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
                            Пары жира быстро забивают теплообменники. Сплит-системы начинают распространять бактерии, плесень и неприятные запахи, вызывая вопросы у Санэпидемстанции.
                        </p>
                    </div>
                </div>

                <div class="p-6 rounded-2xl bg-slate-50 border border-slate-100 flex flex-col justify-between">
                    <div>
                        <div class="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
                            <!-- Dollar/Torn Icon -->
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-1.958-.59-1.171-.88-1.171-2.304 0-3.183 1.171-.88 3.07-.88 4.242 0l.062.047m-3.958 5.02L12 12m0 0H9" />
                            </svg>
                        </div>
                        <h3 class="font-bold text-slate-900 text-sm">Угроза №3: Дорогой ремонт</h3>
                        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
                            Работа забитого кондиционера приводит к перегрузке компрессора. Его замена обходится в 45 000+ сомов, а покупка новой системы — еще дороже.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Value Prop Banner -->
            <div class="mt-10 p-6 rounded-2xl bg-blue-600 text-white flex items-center justify-between">
                <div class="max-w-[70%]">
                    <h3 class="font-bold text-base">Своевременная профилактика экономит бюджет в 3-4 раза!</h3>
                    <p class="text-[11px] text-blue-100 mt-1 leading-relaxed">
                        Регулярная чистка и дозаправка фреоном предотвращают 90% поломок компрессора и продлевают срок службы техники на 5-7 лет.
                    </p>
                </div>
                <div class="text-right">
                    <span class="text-xs uppercase tracking-widest text-blue-200 block font-semibold">Ваша Экономия</span>
                    <span class="text-3xl font-extrabold">до 70%</span>
                </div>
            </div>
        </div>

        <!-- Page 1 Footer -->
        <div class="flex justify-between items-center text-xs text-slate-400 border-t pt-4 border-slate-100 mt-auto">
            <span>Коммерческое предложение | ClimaFlow</span>
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
                <span class="text-xs text-slate-400">Эксклюзивное предложение</span>
            </div>

            <!-- Financial Comparison Table -->
            <div class="mt-10">
                <h2 class="text-xl font-bold text-slate-900 tracking-tight">Экономика вопроса: почему выгодно обслуживать, а не чинить</h2>
                <p class="text-xs text-slate-500 mt-1">Ниже приведено реальное сравнение затрат на содержание климатической техники:</p>
                
                <table class="w-full mt-6 text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 border-b border-slate-100">
                            <th class="p-3 text-xs font-bold uppercase text-slate-600 tracking-wider">Тип услуги</th>
                            <th class="p-3 text-xs font-bold uppercase text-slate-600 tracking-wider">Стоимость</th>
                            <th class="p-3 text-xs font-bold uppercase text-slate-600 tracking-wider">Что вы получаете</th>
                        </tr>
                    </thead>
                    <tbody class="text-xs divide-y divide-slate-100">
                        <tr>
                            <td class="p-3 font-semibold text-slate-900">Профилактическое ТО ClimaFlow</td>
                            <td class="p-3 text-blue-600 font-bold">от 1 200 сом</td>
                            <td class="p-3 text-slate-500">Полная чистка от жира, антибактериальная обработка, дозаправка фреоном. Спокойствие на весь сезон.</td>
                        </tr>
                        <tr>
                            <td class="p-3 font-semibold text-slate-900">Ремонт или замена компрессора</td>
                            <td class="p-3 text-red-600 font-bold">от 25 000 сом</td>
                            <td class="p-3 text-slate-500">Экстренные расходы, простой ресторана, покупка дорогих запчастей.</td>
                        </tr>
                        <tr>
                            <td class="p-3 font-semibold text-slate-900">Покупка нового кондиционера</td>
                            <td class="p-3 text-red-700 font-bold">от 60 000 сом</td>
                            <td class="p-3 text-slate-500">Полная замена оборудования + оплата монтажа сплит-системы.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Our Zero-Risk Offer -->
            <div class="mt-10 p-8 rounded-2xl bg-slate-50 border border-blue-100 relative overflow-hidden">
                <div class="absolute -right-16 -top-16 w-36 h-36 rounded-full bg-blue-100/30 -z-0"></div>
                <div class="relative z-10">
                    <span class="text-[10px] font-bold uppercase tracking-widest text-blue-600 bg-blue-50 px-3 py-1 rounded-full">Наш лид-магнит</span>
                    <h2 class="text-2xl font-extrabold text-slate-900 mt-3">Полная диагностика кондиционеров — 0 сом</h2>
                    <p class="text-xs text-slate-600 mt-2 leading-relaxed">
                        Мы бесплатно приедем в ваше кафе или ресторан в удобное время и проведем диагностику внутренних и наружных блоков. Это **абсолютно бесплатно** и **ни к чему вас не обязывает**.
                    </p>
                    
                    <div class="grid grid-cols-2 gap-4 mt-6">
                        <div class="flex items-start gap-2">
                            <span class="text-blue-600 font-bold text-sm">✓</span>
                            <span class="text-xs text-slate-600 font-medium">Замер рабочего давления и уровня фреона</span>
                        </div>
                        <div class="flex items-start gap-2">
                            <span class="text-blue-600 font-bold text-sm">✓</span>
                            <span class="text-xs text-slate-600 font-medium">Проверка пусковых токов компрессора</span>
                        </div>
                        <div class="flex items-start gap-2">
                            <span class="text-blue-600 font-bold text-sm">✓</span>
                            <span class="text-xs text-slate-600 font-medium">Осмотр дренажной системы и чистоты фильтров</span>
                        </div>
                        <div class="flex items-start gap-2">
                            <span class="text-blue-600 font-bold text-sm">✓</span>
                            <span class="text-xs text-slate-600 font-medium">Диагностика электрических соединений</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Call to Action Section -->
            <div class="mt-12 text-center">
                <h3 class="font-bold text-slate-900 text-sm">Готовы обезопасить свой бизнес перед сезоном?</h3>
                <p class="text-xs text-slate-500 mt-1">Свяжитесь с нами прямо сейчас и забронируйте удобное время для визита мастера</p>
                
                <div class="mt-6 flex flex-col items-center gap-4">
                    <!-- CTA Button -->
                    <a href="https://wa.me/996502985896?text=Хочу%20бесплатную%20диагностику" class="px-8 py-3.5 rounded-xl bg-blue-600 text-white font-bold text-xs uppercase tracking-wider hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/20 inline-block font-montserrat">
                        Записаться на бесплатную диагностику (0 сом)
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
            <span>Коммерческое предложение | ClimaFlow</span>
            <span class="font-semibold text-slate-500">Страница 2 из 2</span>
        </div>
    </div>

</body>
</html>
"""

def generate_pdf():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Записываем HTML-файл во временную директорию
    html_path = os.path.join(script_dir, "kp.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"Временный HTML-файл записан в {html_path}")
    
    pdf_path = os.path.join(script_dir, "kp_climaflow.pdf")
    
    with sync_playwright() as p:
        print("Запуск браузера для генерации PDF...")
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context()
        page = context.new_page()
        
        # Загружаем локальный HTML
        page.goto(f"file://{html_path}")
        
        # Ждем загрузки стилей и шрифтов
        print("Ожидание завершения загрузки ресурсов...")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000) # Даем время на рендер шрифтов Google Fonts
        
        # Генерируем A4 PDF
        print("Экспорт в PDF...")
        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
        )
        
        browser.close()
    
    # Удаляем временный HTML-файл
    if os.path.exists(html_path):
        os.remove(html_path)
        
    print(f"Успешно сгенерирован PDF-файл: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
