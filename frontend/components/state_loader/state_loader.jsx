import React from 'react';

class StateLoader extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        this.props.updateTipsCusips()
            .then(() => {this.props.referenceData.tips.cusips.map(cusip => this.props.updateTipsRefData(cusip)) });
        this.props.updateTipsPrices();
        this.props.updateTsyRefData();
        this.props.updateOtrTsyQuotesWsj();
    }

    render() {
        return (<div id="stateLoader"></div>);
    }
}

export default StateLoader;
