import React from 'react';

class StateLoader extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        this.props.updateTipsCusips()
            .then(() => {this.props.referenceData.tips.cusips.map(cusip => this.props.updateTipsRefData(cusip)) });
        this.props.updateTipsPrices();
        this.props.updateOtrTipsQuotesCnbc();
        this.props.updateTsyRefData();
        this.props.updateOtrTsyQuotesCnbc();
        this.props.updateOtrTsyQuotesWsj();
        this.props.updateOtrTsyQuotesMw();
        this.props.updateOtrTsyQuotesCme();
        
        // Bond futures quotes
        this.props.updateBondFuturesQuotesCme('CME 2Y UST Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 3Y UST Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 5Y UST Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 10Y UST Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 20Y UST Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 30Y UST Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME Ultra-10Y UST Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME Ultra-30Y UST Futures (intraday)');
        //this.props.updateBondFuturesQuotesCme('CME 2Y Micro-yield Futures (intraday)');
        //this.props.updateBondFuturesQuotesCme('CME 5Y Micro-yield Futures (intraday)');
        //this.props.updateBondFuturesQuotesCme('CME 10Y Micro-yield Futures (intraday)');
        //this.props.updateBondFuturesQuotesCme('CME 30Y Micro-yield Futures (intraday)');
    }

    render() {
        return (<div id="stateLoader"></div>);
    }
}

export default StateLoader;
