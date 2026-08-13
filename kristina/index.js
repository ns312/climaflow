document.addEventListener('DOMContentLoaded', () => {

    /* ==========================================
       🖼️ GALLERY FILTER LOGIC
       ========================================== */
    const filterButtons = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.portfolio-item');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            button.classList.add('active');

            const filterValue = button.getAttribute('data-filter');

            galleryItems.forEach(item => {
                const itemCategory = item.getAttribute('data-category');
                
                if (filterValue === 'all' || itemCategory === filterValue) {
                    item.style.display = 'block';
                    // Trigger a brief fade-in animation
                    item.style.opacity = '0';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transition = 'opacity 0.4s ease';
                    }, 50);
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    /* ==========================================
       🏷️ PACKAGE SELECTION LINKING
       ========================================== */
    const selectPackageButtons = document.querySelectorAll('.select-pack');
    const packageSelectDropdown = document.getElementById('package');

    selectPackageButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const packageName = button.getAttribute('data-package');
            
            // Set select dropdown value
            if (packageSelectDropdown) {
                packageSelectDropdown.value = packageName;
            }

            // Scroll to the booking form
            const bookingSection = document.getElementById('booking');
            if (bookingSection) {
                bookingSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    /* ==========================================
       📩 WHATSAPP FORM REDIRECT LOGIC
       ========================================== */
    const leadForm = document.getElementById('leadForm');
    const whatsappNumber = '996502500874'; // Твой номер WhatsApp

    if (leadForm) {
        leadForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const clientName = document.getElementById('name').value.trim();
            const selectedPackage = document.getElementById('package').value;
            const clientMessage = document.getElementById('message').value.trim();

            if (!clientName || !selectedPackage) {
                alert('Пожалуйста, заполните имя и выберите пакет.');
                return;
            }

            // Формируем красивый текст для WhatsApp
            let text = `Здравствуйте, Кристина! Меня зовут ${clientName}. \n\n`;
            text += `Хочу обсудить фотосессию по пакету: *"${selectedPackage}"*.\n`;
            
            if (clientMessage) {
                text += `Пожелания к съемке: ${clientMessage}`;
            }

            // Кодируем текст для URL
            const encodedText = encodeURIComponent(text);
            const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodedText}`;

            // Перенаправляем пользователя в WhatsApp
            window.open(whatsappUrl, '_blank');
        });
    }
});
