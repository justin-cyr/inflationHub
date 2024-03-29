import { RECEIVE_TIPS_CUSIPS, RECEIVE_TIPS_REF_DATA, RECEIVE_TSY_REF_DATA } from "../actions/referenceData";
import { RECEIVE_OTR_TIPS_QUOTES_CNBC, RECEIVE_OTR_TSY_QUOTES_CNBC } from "../actions/quotesDaily";

const cnbcLogo = "https://upload.wikimedia.org/wikipedia/commons/e/e3/CNBC_logo.svg";
const wsjLogo = "https://www.redledges.com/wp-content/uploads/2021/09/WSJ-logo-black.jpeg";
const mwLogo = "https://www.saashub.com/images/app/service_logos/19/47ac30a4ded4/medium.png?1542368413";
const cmeLogo = "https://ffnews.com/wp-content/uploads/2022/03/1625171625444.jpg";
const yfLogo = "https://s.yimg.com/cv/apiv2/default/20211027/logo-18-18.svg";

const benchmarkTsys = [
    'US 1M',
    'US 2M',
    'US 3M',
    'US 4M',
    'US 6M',
    'US 1Y',
    'US 2Y',
    'US 3Y',
    'US 5Y',
    'US 7Y',
    'US 10Y',
    'US 20Y',
    'US 30Y'
];

const benchmarkTips = [
    'TIPS 5Y',
    'TIPS 10Y',
    'TIPS 30Y'
];

// default state
const _emptyState = {
    logos: { cnbc: cnbcLogo, wsj: wsjLogo, mw: mwLogo, cme: cmeLogo, yf: yfLogo },
    tips: { cusips: [], otr: {}, bonds: {}, benchmarkTips: benchmarkTips },
    tsys: { cusips: [], otr: {}, bonds: {}, benchmarkTsys: benchmarkTsys },
}

// helper function for OTR reference data update
const newOtrBondRefData = (currentOtrBonds, responseData) => {
    const data = responseData;
    let newOtrBonds = currentOtrBonds;

    // Update quotes for the first time or replace older quotes
    for (let record of data) {
        const quoteTime = new Date(record.timestamp)
        if (!(record.standardName in currentOtrBonds) ||
            (quoteTime > currentOtrBonds[record.standardName].timestamp)) {

            newOtrBonds[record.standardName] = {
                name: record.name,
                maturityDate: record.maturityDate,
                coupon: Number(record.coupon),
                timestamp: quoteTime
            }
        }
        else {
            // keep existing quote
            newOtrBonds[record.standardName] = currentOtrBonds[record.standardName];
        }
    }

    return newOtrBonds;
};

// Reference data reducer
export default (state = _emptyState, action) => {
    Object.freeze(state);
    switch (action.type) {

        case RECEIVE_TIPS_CUSIPS:
            return {
                ...state,
                tips: {
                    ...state.tips,
                    cusips: action.response.cusips
                }
            };
        
        case RECEIVE_TIPS_REF_DATA:
            const cusip = action.response.referenceData.cusip;
            return {
                ...state,
                tips: {
                    ...state.tips,
                    bonds: {
                        ...state.tips.bonds,
                        [cusip]: action.response.referenceData
                    }
                }
            };

        case RECEIVE_TSY_REF_DATA:
            return {
                ...state,
                tsys: {
                    ...state.tsys,
                    cusips: action.response.referenceData.cusips,
                    bonds: action.response.referenceData.bonds
                }
            }

        case RECEIVE_OTR_TSY_QUOTES_CNBC:
        {
            const newOtrTsys = newOtrBondRefData(state.tsys.otr, action.response.data);

            return {
                ...state,
                tsys: {
                    ...state.tsys,
                    otr: newOtrTsys
                }
            }
        }

        case RECEIVE_OTR_TIPS_QUOTES_CNBC:
            {
                const newOtrTips = newOtrBondRefData(state.tips.otr, action.response.data);

                return {
                    ...state,
                    tips: {
                        ...state.tips,
                        otr: newOtrTips
                    }
                }
            }

        default:
            return state;
    }
}
