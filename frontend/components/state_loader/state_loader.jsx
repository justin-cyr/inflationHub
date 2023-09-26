import React from 'react';

class StateLoader extends React.Component {
    constructor(props) {
        super(props);

        const yfConn = new WebSocket('wss://streamer.finance.yahoo.com');
        yfConn.onopen = (e) => { 
            console.log('Connection open');
            yfConn.send(JSON.stringify({ 'subscribe': ['JPY=X', 'BTC-USD'] }));
        };
        yfConn.onmessage = (e) => this.props.updateYfWsQuote(e);

        this.state = {
            yfConn: yfConn
        }
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
        this.props.updateBondFuturesQuotesCme('CME 2Y Micro-yield Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 5Y Micro-yield Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 10Y Micro-yield Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 30Y Micro-yield Futures (intraday)');

        // IR futures quotes
        this.props.updateBondFuturesQuotesCme('CME 3M SOFR Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 1M SOFR Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('CME 30D FF Futures (intraday)');
        this.props.updateBondFuturesQuotesCme('Eris Swap Futures (intraday)');
    }

    componentWillUnmount() {
        this.state.yfConn.close();
    }

    render() {
        return (<div id="stateLoader"></div>);
    }
}

export default StateLoader;
