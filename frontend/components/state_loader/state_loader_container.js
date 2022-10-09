import { connect } from 'react-redux';
import { updateTipsPrices } from '../../actions/quotesDaily';
import StateLoader from './state_loader';

const mapDispatchToProps = dispatch => ({
    updateTipsPrices: () => dispatch(updateTipsPrices())
});

export default connect(null, mapDispatchToProps)(StateLoader);
