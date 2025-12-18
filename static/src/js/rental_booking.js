/* MyBike Store - JavaScript interactif */

odoo.define('mybike_store.rental_booking', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    // Widget pour le calcul automatique du prix de location
    publicWidget.registry.RentalPriceCalculator = publicWidget.Widget.extend({
        selector: '.rental-booking-form',
        events: {
            'change select[name="bike_id"]': '_onBikeChange',
            'change select[name="rental_type"]': '_onRentalTypeChange',
            'change input[name="start_date"]': '_onDateChange',
            'change input[name="end_date"]': '_onDateChange',
        },

        start: function () {
            this._super.apply(this, arguments);
            this._updatePrice();
        },

        _onBikeChange: function () {
            this._updatePrice();
            this._loadBikeDetails();
        },

        _onRentalTypeChange: function () {
            this._updatePrice();
        },

        _onDateChange: function () {
            this._updatePrice();
        },

        _loadBikeDetails: function () {
            var bikeId = this.$('select[name="bike_id"]').val();
            if (!bikeId) return;

            var $bikeInfo = this.$('.bike-info-container');
            $bikeInfo.html('<div class="text-center"><i class="fa fa-spinner fa-spin"></i> Chargement...</div>');

            // Simuler le chargement des détails (à remplacer par un appel AJAX réel)
            setTimeout(function() {
                $bikeInfo.html(`
                    <div class="bike-details">
                        <h4>Informations du vélo</h4>
                        <p><strong>Caution:</strong> 200€</p>
                        <p><strong>État:</strong> Excellent</p>
                        <p><strong>Assurance:</strong> Disponible (+5€/jour)</p>
                    </div>
                `);
            }, 500);
        },

        _updatePrice: function () {
            var bikeId = this.$('select[name="bike_id"]').val();
            var rentalType = this.$('select[name="rental_type"]').val();
            var startDate = this.$('input[name="start_date"]').val();
            var endDate = this.$('input[name="end_date"]').val();

            if (!bikeId || !rentalType || !startDate || !endDate) {
                this.$('.price-summary').hide();
                return;
            }

            // Calculer la durée
            var start = new Date(startDate);
            var end = new Date(endDate);
            var diffTime = Math.abs(end - start);
            var diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
            var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            // Prix de base (à récupérer dynamiquement du vélo sélectionné)
            var prices = {
                'hour': 5,
                'day': 15,
                'week': 60,
                'month': 200
            };

            var unitPrice = prices[rentalType] || 0;
            var totalPrice = 0;

            if (rentalType === 'hour') {
                totalPrice = unitPrice * diffHours;
            } else if (rentalType === 'day') {
                totalPrice = unitPrice * diffDays;
            } else if (rentalType === 'week') {
                var weeks = Math.ceil(diffDays / 7);
                totalPrice = unitPrice * weeks;
            } else if (rentalType === 'month') {
                var months = Math.ceil(diffDays / 30);
                totalPrice = unitPrice * months;
            }

            // Afficher le récapitulatif
            this.$('.price-summary').show();
            this.$('.duration-display').text(this._formatDuration(diffHours));
            this.$('.price-display').text(totalPrice.toFixed(2) + ' €');
        },

        _formatDuration: function (hours) {
            if (hours < 24) {
                return hours + ' heure' + (hours > 1 ? 's' : '');
            }
            var days = Math.floor(hours / 24);
            return days + ' jour' + (days > 1 ? 's' : '');
        },
    });

    // Widget pour l'affichage de la disponibilité
    publicWidget.registry.BikeAvailabilityChecker = publicWidget.Widget.extend({
        selector: '.bike-availability-check',
        events: {
            'click .check-availability-btn': '_checkAvailability',
        },

        _checkAvailability: function (ev) {
            ev.preventDefault();
            var $btn = $(ev.currentTarget);
            var bikeId = $btn.data('bike-id');

            $btn.html('<i class="fa fa-spinner fa-spin"></i> Vérification...');
            $btn.prop('disabled', true);

            // Simuler vérification (à remplacer par appel AJAX)
            setTimeout(function() {
                $btn.html('<i class="fa fa-check"></i> Disponible');
                $btn.removeClass('btn-primary').addClass('btn-success');
            }, 1000);
        },
    });

    // Smooth scroll pour les liens d'ancre
    $(document).ready(function() {
        $('a[href^="#"]').on('click', function(e) {
            var target = $(this.getAttribute('href'));
            if(target.length) {
                e.preventDefault();
                $('html, body').stop().animate({
                    scrollTop: target.offset().top - 80
                }, 800);
            }
        });

        // Animation au scroll
        var observerOptions = {
            threshold: 0.1
        };

        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.bike-card, .feature-card').forEach(function(el) {
            observer.observe(el);
        });
    });

    return {
        RentalPriceCalculator: publicWidget.registry.RentalPriceCalculator,
        BikeAvailabilityChecker: publicWidget.registry.BikeAvailabilityChecker,
    };
});
