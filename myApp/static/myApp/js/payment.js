document.addEventListener('DOMContentLoaded', function() {
    // Format card number with spaces
    const cardNumberInput = document.getElementById('card_number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
            let formattedValue = '';
            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) {
                    formattedValue += ' ';
                }
                formattedValue += value[i];
            }
            e.target.value = formattedValue;
        });
    }

    // Format expiry date as MM/YY
    const expiryDateInput = document.getElementById('expiry_date');
    if (expiryDateInput) {
        expiryDateInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }

    // Credit functionality
    const useCreditCheckbox = document.getElementById('use_credit');
    const creditUsedInput = document.getElementById('credit_used');
    const creditAppliedDisplay = document.getElementById('credit_applied');
    const totalAmountDisplay = document.getElementById('total_amount');
    
    if (totalAmountDisplay) {
        const ticketPriceText = totalAmountDisplay.textContent.replace('€', '');
        const ticketPrice = parseFloat(ticketPriceText);
        const maxCreditElement = document.querySelector('.credit-amount small');
        const maxCredit = maxCreditElement ? 
            parseFloat(maxCreditElement.textContent.replace('Available credit: €', '')) : 0;

        if (useCreditCheckbox && creditUsedInput) {
            // Initialize credit input as disabled
            creditUsedInput.disabled = !useCreditCheckbox.checked;
            
            useCreditCheckbox.addEventListener('change', function() {
                creditUsedInput.disabled = !this.checked;
                if (!this.checked) {
                    creditUsedInput.value = '0';
                    updateSummary(0);
                } else {
                    creditUsedInput.value = Math.min(ticketPrice, maxCredit).toFixed(2);
                    updateSummary(parseFloat(creditUsedInput.value));
                }
            });

            creditUsedInput.addEventListener('input', function() {
                let value = parseFloat(this.value) || 0;
                if (value > maxCredit) {
                    value = maxCredit;
                    this.value = maxCredit.toFixed(2);
                }
                if (value > ticketPrice) {
                    value = ticketPrice;
                    this.value = ticketPrice.toFixed(2);
                }
                updateSummary(value);
            });
        }

        function updateSummary(creditApplied) {
            if (creditAppliedDisplay) {
                creditAppliedDisplay.textContent = `-€${creditApplied.toFixed(2)}`;
            }
            if (totalAmountDisplay) {
                const total = Math.max(ticketPrice - creditApplied, 0);
                totalAmountDisplay.textContent = `€${total.toFixed(2)}`;
            }
        }
    }

    // Toggle payment method sections
    const paymentTypeRadios = document.querySelectorAll('input[name="payment_type"]');
    const cardSection = document.getElementById('card_payment_section');
    
    if (paymentTypeRadios.length > 0 && cardSection) {
        paymentTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'credit_card') {
                    cardSection.style.display = 'block';
                } else {
                    cardSection.style.display = 'none';
                }
            });
        });
    }
});