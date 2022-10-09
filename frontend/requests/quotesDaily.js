import $ from 'jquery';

export const getTipsPrices = () => (
    // Request TIPS price data
    $.ajax({
        url: '/tips_prices',
        method: 'GET'
    })
);
