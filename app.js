document.addEventListener('DOMContentLoaded', () => {

  // ==========================================
  // 1. Header scroll effect
  // ==========================================
  const header = document.querySelector('header');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });

  // ==========================================
  // 2. Light / Dark Theme Switcher
  // ==========================================
  const themeToggle = document.getElementById('theme-toggle');
  const sunIcon = document.querySelector('.sun-icon');
  const moonIcon = document.querySelector('.moon-icon');
  const body = document.body;

  const savedTheme = localStorage.getItem('theme') || 'light';
  body.setAttribute('data-theme', savedTheme);
  updateThemeIcons(savedTheme);

  themeToggle.addEventListener('click', () => {
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcons(newTheme);
  });

  function updateThemeIcons(theme) {
    if (theme === 'dark') {
      sunIcon.style.display = 'block';
      moonIcon.style.display = 'none';
    } else {
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'block';
    }
  }

  // ==========================================
  // 3. Interactive AC Visual in Hero
  // ==========================================
  const interactiveAc = document.getElementById('interactive-ac');
  const tempDisplay = document.getElementById('temp-display');
  const modeButtons = document.querySelectorAll('.mode-btn');
  const particlesContainer = document.getElementById('particles-container');

  const modeTemps = {
    cool: '18°C',
    heat: '26°C',
    auto: '22°C'
  };

  modeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      modeButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const mode = btn.dataset.mode;
      interactiveAc.className = `interactive-ac-card glass-card mode-${mode}`;
      tempDisplay.textContent = modeTemps[mode];
      
      particlesContainer.classList.remove('active');
      void particlesContainer.offsetWidth; // Trigger reflow
      particlesContainer.classList.add('active');
    });
  });


  // ==========================================
  // 4. Interactive Services Cost Calculator
  // ==========================================
  const inputQty = document.getElementById('input-qty');
  const qtyVal = document.getElementById('qty-val');
  const resultCost = document.getElementById('result-cost');
  const discountBadge = document.getElementById('discount-badge');
  const calcWhatsappBtn = document.getElementById('calc-whatsapp-btn');
  
  const serviceTypeBtns = document.querySelectorAll('[data-service-type]');
  const acTypeBtns = document.querySelectorAll('[data-ac-class]');

  let selectedService = 'cleaning'; // cleaning, repair, refill, complex
  let selectedAcType = 'wall'; // wall, semi

  const serviceBasePrices = {
    cleaning: 2500,
    repair: 2000,
    refill: 2500,
    complex: 4000
  };

  const serviceNamesRu = {
    cleaning: 'Антибактериальная чистка + дезинфекция',
    repair: 'Срочный ремонт и диагностика',
    refill: 'Дозаправка фреоном',
    complex: 'Комплексное ТО (Чистка + Дозаправка)'
  };

  const acTypeNamesRu = {
    wall: 'бытовых настенных',
    semi: 'полупромышленных (кассетных/напольных)'
  };

  inputQty.addEventListener('input', (e) => {
    qtyVal.textContent = `${e.target.value} шт`;
    calculateCost();
  });

  serviceTypeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      serviceTypeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedService = btn.dataset.serviceType;
      calculateCost();
    });
  });

  acTypeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      acTypeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedAcType = btn.dataset.acClass;
      calculateCost();
    });
  });

  function calculateCost() {
    const qty = parseInt(inputQty.value);
    const basePrice = serviceBasePrices[selectedService];
    
    // Multipliers
    const acMultiplier = selectedAcType === 'semi' ? 1.5 : 1.0;
    
    // Subtotal
    let subtotal = basePrice * qty * acMultiplier;
    
    // Discounts
    let discountPercent = 0;
    if (qty >= 2 && qty < 5) {
      discountPercent = 10; // 10% discount
    } else if (qty >= 5) {
      discountPercent = 15; // 15% discount
    }
    
    let total = subtotal;
    if (discountPercent > 0) {
      total = subtotal * (1 - discountPercent / 100);
      discountBadge.textContent = `Скидка за объем: -${discountPercent}%`;
      discountBadge.style.color = 'var(--color-success)';
    } else {
      discountBadge.textContent = `Скидка за объем не применяется`;
      discountBadge.style.color = 'var(--text-muted)';
    }

    // Animate price change
    animateValue(resultCost, parseInt(resultCost.textContent), Math.round(total), 200);

    // Build dynamic WhatsApp text message
    const serviceName = serviceNamesRu[selectedService];
    const acTypeName = acTypeNamesRu[selectedAcType];
    const messageText = `Здравствуйте! Я рассчитал стоимость обслуживания на сайте ClimaFlow.
Услуга: *${serviceName}*
Количество приборов: *${qty} шт.* (тип: ${acTypeName})
Предварительная стоимость: *${Math.round(total)} сом* ${discountPercent > 0 ? `(Скидка ${discountPercent}%)` : ''}
Хочу записать приборы на обслуживание.`;

    const encodedText = encodeURIComponent(messageText);
    calcWhatsappBtn.href = `https://wa.me/996502985896?text=${encodedText}`;
  }

  function animateValue(obj, start, end, duration) {
    if (start === end) return;
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      obj.innerHTML = Math.floor(progress * (end - start) + start);
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        obj.innerHTML = end;
      }
    };
    window.requestAnimationFrame(step);
  }

  // Initial calculation
  calculateCost();


  // ==========================================
  // 5. Diagnostics Wizard Quiz
  // ==========================================
  const quizSteps = document.querySelectorAll('.quiz-step');
  const quizPrevBtn = document.getElementById('quiz-prev-btn');
  const quizNextBtn = document.getElementById('quiz-next-btn');
  const quizProgressBar = document.getElementById('quiz-progress-bar');
  const quizNavContainer = document.getElementById('quiz-nav-container');
  const quizWhatsappSubmit = document.getElementById('quiz-whatsapp-submit');

  let currentStep = 1;
  const totalSteps = quizSteps.length;
  const quizAnswers = {};

  const optionLabelsRu = {
    // Step 1
    'no-cool': 'Плохо охлаждает / теплый воздух',
    'leak': 'Капает/течет вода',
    'smell': 'Неприятный запах плесени/пыли',
    'no-power': 'Не включается вообще',
    // Step 2
    'wall-mount': 'Бытовой настенный',
    'cassette': 'Потолочный / Кассетный',
    'floor': 'Напольный / Колонный',
    'multi': 'Мульти-сплит система',
    // Step 3
    'urgent': 'Срочно (в течение часа)',
    'today': 'Сегодня в удобное время',
    'tomorrow': 'Завтра или позже',
    'consult': 'Просто узнать цену / консультация',
    // Step 4
    'center': 'Центр Бишкека',
    'micro': 'Микрорайоны',
    'suburb': 'Пригород Бишкека (до 15 км)',
    'office-location': 'Офис / Коммерция'
  };

  document.querySelectorAll('.quiz-step .option-card').forEach(card => {
    card.addEventListener('click', () => {
      const parentStep = card.closest('.quiz-step');
      const stepIndex = parentStep.dataset.step;
      
      parentStep.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');

      quizAnswers[`step-${stepIndex}`] = card.dataset.val;

      // Auto-advance
      if (currentStep < totalSteps - 1) {
        setTimeout(() => {
          advanceStep(1);
        }, 300);
      }
    });
  });

  quizNextBtn.addEventListener('click', () => {
    advanceStep(1);
  });

  quizPrevBtn.addEventListener('click', () => {
    advanceStep(-1);
  });

  function advanceStep(direction) {
    if (direction > 0 && currentStep < totalSteps - 1) {
      const activeStepEl = document.querySelector(`.quiz-step[data-step="${currentStep}"]`);
      const isSelected = activeStepEl.querySelector('.option-card.selected');
      if (!isSelected) {
        alert('Пожалуйста, выберите один из вариантов, чтобы продолжить.');
        return;
      }
    }

    document.querySelector(`.quiz-step[data-step="${currentStep}"]`).classList.remove('active');
    currentStep += direction;
    
    const newStepEl = document.querySelector(`.quiz-step[data-step="${currentStep}"]`);
    newStepEl.classList.add('active');

    const progressPercent = ((currentStep - 1) / (totalSteps - 1)) * 100;
    quizProgressBar.style.width = `${progressPercent}%`;

    quizPrevBtn.style.visibility = currentStep > 1 && currentStep < totalSteps ? 'visible' : 'hidden';
    
    if (currentStep === totalSteps - 1) {
      quizNextBtn.textContent = 'Узнать результат';
      quizNextBtn.style.display = 'inline-flex';
    } else if (currentStep === totalSteps) {
      quizNextBtn.style.display = 'none';
      quizNavContainer.style.display = 'none';
      buildQuizWhatsAppLink();
    } else {
      quizNextBtn.textContent = 'Далее';
      quizNextBtn.style.display = 'inline-flex';
    }
  }

  function buildQuizWhatsAppLink() {
    const issueVal = optionLabelsRu[quizAnswers['step-1']];
    const typeVal = optionLabelsRu[quizAnswers['step-2']];
    const urgencyVal = optionLabelsRu[quizAnswers['step-3']];
    const locationVal = optionLabelsRu[quizAnswers['step-4']];

    const messageText = `Здравствуйте! Я прошел онлайн-диагностику кондиционера на сайте ClimaFlow.
Вот результаты диагностики:
1. Какая проблема: *${issueVal}*
2. Тип прибора: *${typeVal}*
3. Срочность: *${urgencyVal}*
4. Локация: *${locationVal}*

Хочу закрепить за собой скидку 10%, узнать точную цену и вызвать мастера.`;

    const encodedText = encodeURIComponent(messageText);
    quizWhatsappSubmit.addEventListener('click', () => {
      window.open(`https://wa.me/996502985896?text=${encodedText}`, '_blank');
    });
  }


  // Google reviews are displayed statically, no slider JS needed here.


  // ==========================================
  // 7. Quick Lead Capture Form Redirect to WhatsApp
  // ==========================================
  const mainContactForm = document.getElementById('main-contact-form');

  mainContactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('contact-name').value;
    const phone = document.getElementById('contact-phone').value;

    const messageText = `Здравствуйте! Меня зовут *${name}*.
Я оставил заявку на сайте ClimaFlow по ремонту/чистке кондиционера.
Мой контактный номер телефона: *${phone}*.
Пожалуйста, перезвоните мне для консультации и согласования выезда мастера.`;

    const encodedText = encodeURIComponent(messageText);
    window.open(`https://wa.me/996502985896?text=${encodedText}`, '_blank');
  });

  // Phone prefix auto helper
  const contactPhoneField = document.getElementById('contact-phone');
  if (contactPhoneField) {
    contactPhoneField.addEventListener('focus', () => {
      if (contactPhoneField.value.trim() === '' || contactPhoneField.value === '+996 ') {
        contactPhoneField.value = '+996 ';
      }
    });
    contactPhoneField.addEventListener('blur', () => {
      if (contactPhoneField.value === '+996 ') {
        contactPhoneField.value = '';
      }
    });
  }

  // ==========================================
  // 8. Problems Slider for Mobile
  // ==========================================
  const problemsGrid = document.getElementById('problems-grid');
  const problemsPrev = document.getElementById('problems-prev');
  const problemsNext = document.getElementById('problems-next');
  const problemsDotsContainer = document.getElementById('problems-dots');
  const problemCards = document.querySelectorAll('.problem-card');
  
  let currentProblemIdx = 0;
  const totalProblems = problemCards.length;

  // Initialize dots
  if (problemsDotsContainer) {
    problemsDotsContainer.innerHTML = '';
    for (let i = 0; i < totalProblems; i++) {
      const dot = document.createElement('span');
      dot.className = `dot ${i === 0 ? 'active' : ''}`;
      dot.dataset.index = i;
      problemsDotsContainer.appendChild(dot);
      
      dot.addEventListener('click', () => {
        currentProblemIdx = i;
        slideProblems();
      });
    }
  }

  function slideProblems() {
    if (window.innerWidth <= 768) {
      problemsGrid.style.transform = `translateX(-${currentProblemIdx * 100}%)`;
      
      const dots = problemsDotsContainer.querySelectorAll('.dot');
      dots.forEach((dot, idx) => {
        if (idx === currentProblemIdx) {
          dot.classList.add('active');
        } else {
          dot.classList.remove('active');
        }
      });
    } else {
      problemsGrid.style.transform = 'none';
    }
  }

  if (problemsNext) {
    problemsNext.addEventListener('click', () => {
      currentProblemIdx = (currentProblemIdx + 1) % totalProblems;
      slideProblems();
    });
  }

  if (problemsPrev) {
    problemsPrev.addEventListener('click', () => {
      currentProblemIdx = (currentProblemIdx - 1 + totalProblems) % totalProblems;
      slideProblems();
    });
  }

  // Swipe/Touch support
  let touchStartX = 0;
  let touchEndX = 0;
  
  problemsGrid.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });
  
  problemsGrid.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }, { passive: true });
  
  function handleSwipe() {
    if (window.innerWidth > 768) return;
    const threshold = 50;
    if (touchStartX - touchEndX > threshold) {
      currentProblemIdx = (currentProblemIdx + 1) % totalProblems;
      slideProblems();
    } else if (touchEndX - touchStartX > threshold) {
      currentProblemIdx = (currentProblemIdx - 1 + totalProblems) % totalProblems;
      slideProblems();
    }
  }

  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
      problemsGrid.style.transform = 'none';
    } else {
      slideProblems();
    }
  });

  // ==========================================
  // 9. Google Ads & Analytics Conversion Tracking
  // ==========================================
  function trackEvent(eventName, category) {
    if (typeof gtag === 'function') {
      gtag('event', eventName, {
        'event_category': category,
        'event_label': window.location.pathname
      });
      console.log(`[ClimaFlow Track] Event sent: ${eventName}`);
    } else {
      console.log(`[ClimaFlow Track] Event logged: ${eventName} (Google tag not loaded yet)`);
    }
  }

  // Отслеживание кликов по всем ссылкам WhatsApp
  document.querySelectorAll('a[href*="wa.me"]').forEach(link => {
    link.addEventListener('click', () => {
      trackEvent('click_whatsapp', 'Lead');
    });
  });

  // Отслеживание кликов по всем кнопкам «Позвонить»
  document.querySelectorAll('a[href^="tel:"]').forEach(link => {
    link.addEventListener('click', () => {
      trackEvent('click_phone', 'Lead');
    });
  });

  // Отслеживание отправки контактной формы
  const leadForm = document.getElementById('main-contact-form');
  if (leadForm) {
    leadForm.addEventListener('submit', () => {
      trackEvent('submit_lead_form', 'Form');
    });
  }
});

