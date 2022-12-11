import { connect } from 'react-redux';
import CurveViewer from './curve_viewer';

const mapStateToProps = state => ({
    referenceData: state.referenceData,
    quotes: state.quotes
});

export default connect(mapStateToProps)(CurveViewer);
