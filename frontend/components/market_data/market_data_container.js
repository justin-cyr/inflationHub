import { connect } from 'react-redux';
import MarketData from './market_data';

const mapStateToProps = state => ({
    referenceData: state.referenceData,
    quotes: state.quotes
});

export default connect(mapStateToProps)(MarketData);
