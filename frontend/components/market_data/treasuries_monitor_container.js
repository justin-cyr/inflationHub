import { connect } from 'react-redux';
import TreasuriesMonitor from './treasuries_monitor';

const mapStateToProps = state => ({
    referenceData: state.referenceData,
    quotes: state.quotes
});

export default connect(mapStateToProps)(TreasuriesMonitor);