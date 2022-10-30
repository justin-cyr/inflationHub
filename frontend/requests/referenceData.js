import $ from 'jquery';

export const getTipsCusips = () => (
    // Request TIPS CUSIPs
    $.ajax({
        url: '/tips_cusips',
        method: 'GET'
    })
);

export const getTipsRefData = cusip => (
    $.ajax({
        url: '/tips_reference_data/' + cusip,
        method: 'GET'
    })
);

export const getTsyRefData = () => (
    $.ajax({
        url: '/all_tsy_reference_data',
        method: 'GET'
    })
);
