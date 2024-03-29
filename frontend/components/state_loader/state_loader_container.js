import { connect } from 'react-redux';
import { updateTipsPrices, updateTipsPricesMw, updateOtrTipsQuotesCnbc, updateOtrTsyQuotesWsj, updateOtrTsyQuotesCnbc, updateOtrTsyQuotesMw, updateOtrTsyQuotesCme, updateBondFuturesQuotesCme, updateYfWsQuote, updateCtdOtrTableCme } from '../../actions/quotesDaily';
import { updateTipsCusips, updateTipsRefData, updateTsyRefData } from '../../actions/referenceData';
import StateLoader from './state_loader';

const mapStateToProps = state => ({
    referenceData: state.referenceData
});

const mapDispatchToProps = dispatch => ({
    updateTipsPrices: () => dispatch(updateTipsPrices()),
    updateTipsPricesMw: (cusips) => dispatch(updateTipsPricesMw(cusips)),
    updateOtrTipsQuotesCnbc: () => dispatch(updateOtrTipsQuotesCnbc()),
    updateOtrTsyQuotesWsj: () => dispatch(updateOtrTsyQuotesWsj()),
    updateOtrTsyQuotesCnbc: () => dispatch(updateOtrTsyQuotesCnbc()),
    updateOtrTsyQuotesMw: () => dispatch(updateOtrTsyQuotesMw()),
    updateOtrTsyQuotesCme: () => dispatch(updateOtrTsyQuotesCme()),
    updateBondFuturesQuotesCme: (dataName) => dispatch(updateBondFuturesQuotesCme(dataName)),
    updateTipsCusips: () => dispatch(updateTipsCusips()),
    updateTipsRefData: cusip => dispatch(updateTipsRefData(cusip)),
    updateTsyRefData: () => dispatch(updateTsyRefData()),
    updateYfWsQuote: (e) => dispatch(updateYfWsQuote(e)),
    updateCtdOtrTableCme: (dataName) => dispatch(updateCtdOtrTableCme(dataName))
});

export default connect(mapStateToProps, mapDispatchToProps)(StateLoader);
