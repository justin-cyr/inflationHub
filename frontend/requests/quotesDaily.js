import $ from 'jquery';

export const getTipsPrices = () => (
    // Request TIPS price data
    $.ajax({
        url: '/tips_prices',
        method: 'GET'
    })
);

export const getOtrTsyQuotesWsj = () => (
    $.ajax({
        url: '/data/WSJ US Treasury Yields (intraday)',
        method: 'GET'
    })
);

