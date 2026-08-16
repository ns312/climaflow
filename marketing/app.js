document.addEventListener('DOMContentLoaded', () => {
    // 1. FAQ Accordion Logic
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            
            // Close all items
            faqItems.forEach(i => i.classList.remove('active'));
            
            // Open clicked item if it wasn't active
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    // 2. Lost Profit Calculator
    const avgCheckInput = document.getElementById('avg-check');
    const searchVolumeInput = document.getElementById('search-volume');
    
    const avgCheckValLabel = document.getElementById('avg-check-val');
    const searchVolumeValLabel = document.getElementById('search-volume-val');
    
    const lostLeadsLabel = document.getElementById('lost-leads-val');
    const lostProfitLabel = document.getElementById('lost-profit-val');

    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    }

    function calculateLostProfit() {
        const avgCheck = parseInt(avgCheckInput.value);
        const searchVolume = parseInt(searchVolumeInput.value);
        
        // Update range labels
        avgCheckValLabel.textContent = `${formatNumber(avgCheck)} сом`;
        searchVolumeValLabel.textContent = `${formatNumber(searchVolume)} запросов`;
        
        // Math formulas:
        // CTR of Search Ads ~ 5%
        // Landing Page Conversion rate ~ 10%
        const potentialClicks = searchVolume * 0.05;
        const potentialLeads = Math.round(potentialClicks * 0.10);
        const lostProfit = potentialLeads * avgCheck;
        
        // Update calculation output
        lostLeadsLabel.textContent = potentialLeads;
        lostProfitLabel.textContent = `${formatNumber(lostProfit)} сом`;
    }

    avgCheckInput.addEventListener('input', calculateLostProfit);
    searchVolumeInput.addEventListener('input', calculateLostProfit);
    
    // Initial run
    calculateLostProfit();

    // 3. Meta Pixel Event Tracking for WhatsApp Clicks
    const waButtons = [
        'header-wa-btn',
        'hero-wa-btn',
        'calc-wa-btn',
        'pack1-wa-btn',
        'pack2-wa-btn',
        'guarantee-wa-btn'
    ];

    waButtons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', () => {
                if (typeof fbq !== 'undefined') {
                    fbq('track', 'Lead', {
                        content_name: 'WhatsApp Click',
                        content_category: 'B2B Lead Generation',
                        value: 40000, // Average expected order value in KGS
                        currency: 'KGS'
                    });
                }
            });
        }
    });

    // 4. Scroll-linked Case Studies Animation Logic
    const caseItems = document.querySelectorAll('.case-scroll-item');
    const casesBg = document.getElementById('cases-bg');
    
    if (caseItems.length > 0 && casesBg) {
        const observerOptions = {
            root: null,
            rootMargin: '-25% 0px -25% 0px', // Trigger when card reaches the middle 50% of the screen
            threshold: 0.15
        };
        
        const caseObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    
                    const targetBg = entry.target.getAttribute('data-bg');
                    if (targetBg) {
                        casesBg.style.backgroundColor = targetBg;
                    }
                } else {
                    entry.target.classList.remove('active');
                    // Reset transform of non-active items
                    const overlapImg = entry.target.querySelector('.case-overlap-img');
                    if (overlapImg) {
                        overlapImg.style.transform = '';
                    }
                }
            });
        }, observerOptions);
        
        caseItems.forEach(item => {
            caseObserver.observe(item);
        });

        // Parallax scroll effect for overlapping 3D graphics
        window.addEventListener('scroll', () => {
            caseItems.forEach(item => {
                if (item.classList.contains('active')) {
                    const rect = item.getBoundingClientRect();
                    const overlapImg = item.querySelector('.case-overlap-img');
                    
                    if (overlapImg) {
                        // Calculate offset from the middle of the screen
                        const centerOffset = (rect.top + rect.height / 2) - (window.innerHeight / 2);
                        
                        // Parallax factors
                        const translateY = centerOffset * 0.18; // vertical shift
                        const rotate = centerOffset * 0.04;    // rotation angle
                        
                        // Apply layout-specific transformations
                        if (item.id === 'case-proforce') {
                            // Left overlap
                            overlapImg.style.transform = `translate3d(calc(-60px + ${translateY * -0.2}px), calc(-50px + ${translateY}px), 0) rotate(${-15 + rotate}deg)`;
                        } else {
                            // Right overlap
                            overlapImg.style.transform = `translate3d(calc(60px + ${translateY * 0.2}px), calc(-50px + ${translateY}px), 0) rotate(${15 + rotate}deg)`;
                        }
                    }
                }
            });
        });
    }

    // 5. Interactive Google Ads Search Mockup Logic
    const mockupTabBtns = document.querySelectorAll('.mockup-tab-btn');
    const searchInputDisplay = document.getElementById('mockup-search-input');
    const adUrl = document.getElementById('mockup-ad-url');
    const adTitle = document.getElementById('mockup-ad-title');
    const adDesc = document.getElementById('mockup-ad-desc');
    const adSitelinksContainer = document.querySelector('.ad-sitelinks');
    
    const mockupData = {
        "пошив одежды оптом бишкек": {
            url: "bazikostyle.com",
            title: "Швейное Производство Оптом в Бишкеке | Фабрика BAZIKO",
            desc: "Швейная фабрика полного цикла. Шьем одежду оптом для маркетплейсов Wildberries и Ozon. Высокое качество, автоматизация, доставка по СНГ. Звоните!",
            sitelinks: ["Договор с гарантией", "Образец за 3 дня", "Цены от фабрики"]
        },
        "спортивные костюмы оптом фабрика": {
            url: "proforce-gcc.com/factory",
            title: "Пошив Спортивной Одежды Оптом от Производителя | PROFORCE",
            desc: "Оптовый пошив спортивных костюмов, худи и брюк на заказ от фабрики PROFORCE. Выгодные цены, премиум ткани, доставка по СНГ. Узнайте прайс!",
            sitelinks: ["Спортивные костюмы", "Худи & Брюки", "Выгодные цены"]
        },
        "ремонт кондиционеров бишкек": {
            url: "climaflow312.com",
            title: "Ремонт и Установка Кондиционеров в Бишкеке | Climaflow",
            desc: "Профессиональный ремонт и установка кондиционеров. Выезд мастера за 30 минут по Бишкеку. Гарантия 1 год. Работаем 24/7. Жмите!",
            sitelinks: ["Выезд за 30 мин", "Гарантия 1 год", "Цены от 1200 сом"]
        }
    };
    
    let typingInterval = null;
    
    function typeText(targetText, callback) {
        if (typingInterval) clearInterval(typingInterval);
        
        let currentText = "";
        let index = 0;
        searchInputDisplay.textContent = "";
        
        typingInterval = setInterval(() => {
            if (index < targetText.length) {
                currentText += targetText[index];
                searchInputDisplay.textContent = currentText;
                index++;
            } else {
                clearInterval(typingInterval);
                if (callback) callback();
            }
        }, 60);
    }
    
    function updateMockupResult(keyword) {
        const data = mockupData[keyword];
        if (data) {
            adUrl.textContent = data.url;
            adTitle.textContent = data.title;
            adDesc.textContent = data.desc;
            
            // Re-render sitelinks
            adSitelinksContainer.innerHTML = "";
            data.sitelinks.forEach(linkText => {
                const span = document.createElement('span');
                span.className = "sitelink";
                span.textContent = linkText;
                adSitelinksContainer.appendChild(span);
            });
        }
    }
    
    if (mockupTabBtns.length > 0 && searchInputDisplay) {
        mockupTabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                mockupTabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const keyword = btn.getAttribute('data-keyword');
                typeText(keyword, () => {
                    updateMockupResult(keyword);
                });
            });
        });
    }

    // 6. Interactive Lead Quiz Logic
    const quizSteps = document.querySelectorAll('.quiz-step');
    const optionBtns = document.querySelectorAll('.quiz-option-btn');
    const progressFill = document.getElementById('quiz-progress');
    const quizSubmitBtn = document.getElementById('quiz-submit-btn');
    
    const quizAnswers = {
        step1: "",
        step2: "",
        step3: "",
        step4: ""
    };
    
    let currentStep = 1;
    const totalSteps = 4;
    
    function showStep(stepNum) {
        quizSteps.forEach(step => step.classList.remove('active'));
        
        if (stepNum === 'final') {
            const finalStepEl = document.getElementById('step-final');
            if (finalStepEl) finalStepEl.classList.add('active');
            if (progressFill) {
                progressFill.style.width = "100%";
                progressFill.textContent = "100%";
            }
        } else {
            const currentStepEl = document.getElementById(`step-${stepNum}`);
            if (currentStepEl) currentStepEl.classList.add('active');
            if (progressFill) {
                const percent = Math.round(((stepNum - 1) / totalSteps) * 100) || 25;
                progressFill.style.width = `${percent}%`;
                progressFill.textContent = `${percent}%`;
            }
        }
    }
    
    if (optionBtns.length > 0) {
        optionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const parentStep = btn.closest('.quiz-step');
                const answer = btn.getAttribute('data-answer');
                
                if (parentStep && answer) {
                    const stepIdStr = parentStep.id; // e.g. "step-1"
                    const stepIndex = parseInt(stepIdStr.split('-')[1]);
                    
                    quizAnswers[`step${stepIndex}`] = answer;
                    
                    if (stepIndex < totalSteps) {
                        currentStep = stepIndex + 1;
                        showStep(currentStep);
                    } else {
                        showStep('final');
                    }
                }
            });
        });
    }
    
    if (quizSubmitBtn) {
        quizSubmitBtn.addEventListener('click', () => {
            const textPayload = `Привет! Я прошел B2B тест на расчет медиаплана Google на вашем сайте Clima Marketing.%0A%0A1. Ниша: ${encodeURIComponent(quizAnswers.step1)}%0A2. Нужная частота продаж: ${encodeURIComponent(quizAnswers.step2)}%0A3. Предыдущий опыт Google Ads: ${encodeURIComponent(quizAnswers.step3)}%0A4. Бюджет на тест: ${encodeURIComponent(quizAnswers.step4)}%0A%0AХочу получить готовый расчет, прогноз кликов и бесплатный аудит 3 конкурентов.`;
            
            const waUrl = `https://wa.me/996502985896?text=${textPayload}`;
            
            // Trigger Meta Lead pixel event tracking
            if (typeof fbq !== 'undefined') {
                fbq('track', 'Lead', {
                    content_name: 'B2B Quiz Submit',
                    value: 0.00,
                    currency: 'USD'
                });
            }
            
            // Redirect
            window.location.href = waUrl;
        });
    }
});

