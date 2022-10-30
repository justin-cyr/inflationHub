import { RECEIVE_TIPS_CUSIPS, RECEIVE_TIPS_REF_DATA, RECEIVE_TSY_REF_DATA } from "../actions/referenceData";
import { RECEIVE_OTR_TIPS_QUOTES_CNBC, RECEIVE_OTR_TSY_QUOTES_CNBC } from "../actions/quotesDaily";

// default state
const _emptyState = {
    tips: { cusips: [], otr: {}, bonds: {} },
    tsys: { cusips: [], otr: {}, bonds: {} },
}

// helper function for OTR reference data update
const newOtrBondRefData = (currentOtrBonds, responseData) => {
    const data = responseData;
    let newOtrBonds = {};

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
