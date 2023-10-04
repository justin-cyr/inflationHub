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
        url: '/data/CNBC US Treasury Yields with 2M, 4M bills (intraday)',
        method: 'GET'
    })
);

export const getOtrTsyQuotesMw = () => (
    $.ajax({
        url: '/data/MW US Treasury Yields (intraday)',
        method: 'GET'
    })
);

export const getOtrTsyQuotesCme = () => (
    $.ajax({
        url: '/data/CME US Treasury Prices (intraday)',
        method: 'GET'
    })
);

export const getOtrTipsQuotesCnbc = () => (
    $.ajax({
        url: '/data/CNBC TIPS Yields (intraday)',
        method: 'GET'
    })
);

export const getBondFuturesQuotesCme = (dataName) => (
    $.ajax({
        url: '/data/' + dataName,
        method: 'GET'
    })
);

export const getData = (dataName) => (
    $.ajax({
        url: '/data/' + dataName,
        method: 'GET'
    })
);
