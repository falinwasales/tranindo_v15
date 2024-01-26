odoo.define('fal_tranindo_ext.ProductScreenInherit', function (require) {
    'use strict';

    const {Gui} = require('point_of_sale.Gui');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const WarningProductScreen = ProductScreen => class extends ProductScreen {

        /**
         * Override the _onClickPay method in the ProductScreen class.
         * Checks if any orderline has a discount with more than 3 decimal places.
         * If so, show an error popup.
         * Otherwise, call the original _onClickPay method.
         */
        async _onClickPay() {
            // Check if any orderline has a discount with more than 3 decimal places
            if (this.env.pos.get_order().orderlines.any(line => line.discount.toString().includes('.') && line.discount.toString().split('.')[1].length > 3)) {
                // Show error popup
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Warning'),
                    body: this.env._t('Discounts with more than 3 decimal places are not supported.'),
                });
            } else {
                // Call the original _onClickPay method
                super._onClickPay();
            }
        }


    };

    Registries.Component.extend(ProductScreen, WarningProductScreen);

    return ProductScreen;
});
