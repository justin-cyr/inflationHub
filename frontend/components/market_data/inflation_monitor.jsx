import React from 'react';

import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';

import EtfTable from './etf_table';

const unchColor = '#bdbdbd'; // default text color
const bbgColor = '#ff6600'; // orange

const tipsBroadEtfs = {
    'TIP': 'Broad',
    'SCHP': 'Broad',
    'SPIP': 'Broad'
};

const tipsCurveEtfs = {
    'VTIP': '0-5Y',
    'STIP': '0-5Y',
    'TDTT': '3Y dur.',
    'TIPX': '1-10Y',
    'LTPZ': '15-30Y',
};

const tipsExoticEtfs = {
    'CPII': 'Near term',
    'RINF': 'Long term',
    'IVOL': 'Volatility'
};


class InflationMonitor extends React.Component {
    constructor(props) {
        super(props);

        this.getChangeColor = this.props.getChangeColor;
    }

    pickQuoteSubset(quotes) {
        let quoteData = {};
        for (let ticker of Object.keys(quotes)) {
            if (ticker in this.props.quotes.daily.yfQuotes) {
                quoteData[ticker] = this.props.quotes.daily.yfQuotes[ticker]
            }
        }
        return quoteData;
    }

    render() {
        // Reference data table
        const loading_data_table = <center>{'... Loading data ...'}</center>;

        // TIPS benchmark table
        let tips_data_table = loading_data_table;
        const tips_table_rows = this.props.referenceData.tips.benchmarkTips.map(standardName =>
            <tr key={standardName}>
                <td style={{
                    textAlign: 'center',
                    color: bbgColor
                }}>{standardName}</td>
                <td style={{
                    textAlign: 'center',
                    color: bbgColor
                }}>{(standardName in this.props.referenceData.tips.otr) ? this.props.referenceData.tips.otr[standardName].maturityDate : ''}</td>
                <td style={{
                    textAlign: 'center',
                    color: bbgColor
                }}>{(standardName in this.props.referenceData.tips.otr) ? this.props.referenceData.tips.otr[standardName].coupon.toFixed(3) + '%' : ''}</td>
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.quotes.daily.tips.otr.cnbc, standardName, 'yieldChange')
                }}>{(standardName in this.props.quotes.daily.tips.otr.cnbc) ? this.props.quotes.daily.tips.otr.cnbc[standardName].yield.toFixed(3) : ''}</td>
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.quotes.daily.tips.otr.cnbc, standardName, 'priceChange')
                }}>{(standardName in this.props.quotes.daily.tips.otr.cnbc) ? this.props.quotes.daily.tips.otr.cnbc[standardName].price.toFixed(3) : ''}</td>
                <td style={{ textAlign: 'center' }}>{(standardName in this.props.quotes.daily.tips.otr.cnbc) ? this.props.quotes.daily.tips.otr.cnbc[standardName].timestamp.toLocaleTimeString() : ''}</td>
            </tr>
        );

        tips_data_table = <div
            style={{ height: '200px', width: '560px', overflow: 'auto' }}
        >
            <Table
                id="tips-benchmark-table"
                responsive
                hover
            >
                <thead>
                    <tr style={{ color: unchColor }}>
                        <th style={{ textAlign: 'center' }}>Name</th>
                        <th style={{ textAlign: 'center' }}>Maturity</th>
                        <th style={{ textAlign: 'center' }}>Coupon</th>
                        <th style={{ textAlign: 'center' }}>YTM
                            <img src={this.props.referenceData.logos.cnbc} width="36" height="24"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>Price
                            <img src={this.props.referenceData.logos.cnbc} width="36" height="24"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>Timestamp</th>
                    </tr>
                </thead>
                <tbody
                    style={{ color: unchColor }}
                >
                    {tips_table_rows}
                </tbody>
            </Table>
        </div>;

        // TIPS ETFs table data
        const tipsBroadEtfData = this.pickQuoteSubset(tipsBroadEtfs);
        const tipsCurveEtfData = this.pickQuoteSubset(tipsCurveEtfs);
        const tipsExoticEtfData = this.pickQuoteSubset(tipsExoticEtfs);

        return (
            <Container fluid>
                <Row>
                    <Col>
                        {/* Tips benchmark table */}
                        <h2>TIPS</h2>
                        {tips_data_table}
                    </Col>
                    <Col>
                        {/* TIPS curve ETF table */}
                        <h2>Curve ETFs</h2>
                        <EtfTable
                            id="tips-curve-etf-table"
                            height="400px"
                            width="560px"
                            etfs={tipsCurveEtfs}
                            data={tipsCurveEtfData}
                            getChangeColor={this.getChangeColor}
                            logo={this.props.referenceData.logos.yf}
                        />
                    </Col>
                </Row>
                <Row>
                    <Col>
                        {/* TIPS broad ETF table */}
                        <h2>Broad ETFs</h2>
                        <EtfTable
                            id="tips-broad-etf-table"
                            height="300px"
                            width="560px"
                            etfs={tipsBroadEtfs}
                            data={tipsBroadEtfData}
                            getChangeColor={this.getChangeColor}
                            logo={this.props.referenceData.logos.yf}
                        />
                    </Col>
                    <Col>
                        {/* TIPS exotic ETF table */}
                        <h2>Exotic ETFs</h2>
                        <EtfTable
                            id="tips-exotic-etf-table"
                            height="300px"
                            width="560px"
                            etfs={tipsExoticEtfs}
                            data={tipsExoticEtfData}
                            getChangeColor={this.getChangeColor}
                            logo={this.props.referenceData.logos.yf}
                        />
                    </Col>
                </Row>
            </Container>
        );
    }
}

export default InflationMonitor;
