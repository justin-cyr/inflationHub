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

export const getOtrTsyQuotesCnbc = () => (
    $.ajax({
        url: '/data/CNBC US Treasury Yields (intraday)',
        method: 'GET'
    })
);

export const getOtrTsyQuotesMw = () => (
    $.ajax({
        url: '/data/MW US Treasury Yields (intraday)',
        method: 'GET'
    })
);
