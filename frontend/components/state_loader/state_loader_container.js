import { connect } from 'react-redux';
import { updateTipsPrices } from '../../actions/quotesDaily';
import { updateTipsCusips, updateTipsRefData } from '../../actions/referenceData';
import StateLoader from './state_loader';

const mapStateToProps = state => ({
    referenceData: state.referenceData
});

const mapDispatchToProps = dispatch => ({
    updateTipsPrices: () => dispatch(updateTipsPrices()),
    updateTipsCusips: () => dispatch(updateTipsCusips()),
    updateTipsRefData: cusip => dispatch(updateTipsRefData(cusip))
});

export default connect(mapStateToProps, mapDispatchToProps)(StateLoader);
