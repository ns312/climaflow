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
                }
            });
        }, observerOptions);
        
        caseItems.forEach(item => {
            caseObserver.observe(item);
        });
    }
});
