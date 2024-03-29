import React from 'react';

import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';

import FuturesTable from './futures_table';

const unchColor = '#bdbdbd'; // default text color
const bbgColor = '#ff6600'; // orange

class BondFuturesMonitor extends React.Component {
    constructor(props) {
        super(props);

        this.getChangeColor = this.props.getChangeColor;
    }

    render() {

        let ctd_table_rows = [<tr><center>{'... Loading data ...'}</center></tr>];
        
        if (this.props.quotes.daily.ctdOtrTable) {
            ctd_table_rows = this.props.quotes.daily.ctdOtrTable.map(record => 
                <tr key={record.futureName}>
                    <td style={{
                        textAlign: 'center',
                        color: bbgColor
                    }}>{record.futureName}</td>
                    <td style={{
                        textAlign: 'center',
                        color: bbgColor
                    }}>{record.standardName}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.getChangeColor({ 'dummy': { 'yieldChange': -record['yieldChange'] } }, 'dummy', 'yieldChange')
                    }}>{record.futurePrice}</td>
                    <td style={{
                        textAlign: 'center',
                    }}>{record.ctdDeliveryDate}</td>
                    <td style={{
                        textAlign: 'center',
                    }}>{record.ctdCoupon.toFixed(3) + '%'}</td>
                    <td style={{
                        textAlign: 'center',
                    }}>{record.ctdMaturity}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.getChangeColor({'dummy': record}, 'dummy', 'yieldChange')
                    }}>{record.fwdYield.toFixed(3)}</td>
                </tr>
            );
        }

        const ctd_otr_table = <div
                style={{overflow: 'auto'}}
            >
            <Table
                id="ctd-otr-table"
                responsive
                hover
            >
                <thead style={{ color: unchColor }}>
                    <tr>
                        <th style={{ textAlign: 'center' }}>Name</th>
                        <th style={{ textAlign: 'center' }}>Ticker</th>
                        <th style={{ textAlign: 'center' }}>Price
                            <img src={this.props.referenceData.logos.cme} width="30" height="30"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>Delivery Date</th>
                        <th style={{ textAlign: 'center' }}>CTD Cpn</th>
                        <th style={{ textAlign: 'center' }}>CTD Maturity</th>
                        <th style={{ textAlign: 'center' }}>Fwd Yield</th>
                    </tr>
                </thead>
                <tbody
                    style={{ color: unchColor }}
                >
                    {ctd_table_rows}
                </tbody>
            </Table>
        </div>;

        const bond_futures_table_heading = (
            <tr style={{ color: unchColor }}>
                <th style={{ textAlign: 'center' }}>Month</th>
                <th style={{ textAlign: 'center' }}>Ticker</th>
                <th style={{ textAlign: 'center' }}>Price
                    <img src={this.props.referenceData.logos.cme} width="30" height="30"></img>
                </th>
                <th style={{ textAlign: 'center' }}>Last</th>
                <th style={{ textAlign: 'center' }}>Prior Settle</th>
                <th style={{ textAlign: 'center' }}>Volume</th>
                <th style={{ textAlign: 'center' }}>Timestamp</th>
            </tr>
        );

        return (
            <Container fluid>
                <Row>
                    <Col>
                        <h2>Active Futures CTD Bonds</h2>
                            {ctd_otr_table}
                    </Col>
                </Row>
                <Row>
                    <Col>
                        {/* Bond futures table */}
                        <h2>Bond Futures</h2>
                        <div
                            style={{ height: this.props.height, width: '1100px', overflow: 'auto' }}
                        >
                            <Table
                                id="bond-futures-table"
                                responsive
                                hover
                                style={{ color: unchColor }}
                            >
                                <thead>
                                    {bond_futures_table_heading}
                                </thead>
                                <tbody>
                                    <FuturesTable
                                        title="2Y UST Futures"
                                        data={this.props.quotes.daily.futures['CME 2Y UST Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="3Y UST Futures"
                                        data={this.props.quotes.daily.futures['CME 3Y UST Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="5Y UST Futures"
                                        data={this.props.quotes.daily.futures['CME 5Y UST Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="10Y UST Futures"
                                        data={this.props.quotes.daily.futures['CME 10Y UST Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="Ultra-10Y UST Futures"
                                        data={this.props.quotes.daily.futures['CME Ultra-10Y UST Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="20Y UST Futures"
                                        data={this.props.quotes.daily.futures['CME 20Y UST Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="30Y UST Futures"
                                        data={this.props.quotes.daily.futures['CME 30Y UST Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="Ultra-30Y UST Futures"
                                        data={this.props.quotes.daily.futures['CME Ultra-30Y UST Futures (intraday)']}
                                    />
                                </tbody>
                            </Table>
                        </div>
                    </Col>
                </Row>
                <Row>
                    <Col>
                        {/* Micro-yield futures table */}
                        <h2>Micro Yield Futures</h2>
                        <div
                            style={{ height: this.props.height, width: '1100px', overflow: 'auto' }}
                        >
                            <Table
                                id="micro-yield-futures-table"
                                responsive
                                hover
                                style={{ color: unchColor }}
                            >
                                <thead>
                                    {bond_futures_table_heading}
                                </thead>
                                <tbody>
                                    <FuturesTable
                                        title="Micro 2Y-yield Futures"
                                        data={this.props.quotes.daily.futures['CME 2Y Micro-yield Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="Micro 5Y-yield Futures"
                                        data={this.props.quotes.daily.futures['CME 5Y Micro-yield Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="Micro 10Y-yield Futures"
                                        data={this.props.quotes.daily.futures['CME 10Y Micro-yield Futures (intraday)']}
                                    />
                                    <FuturesTable
                                        title="Micro 30Y-yield Futures"
                                        data={this.props.quotes.daily.futures['CME 30Y Micro-yield Futures (intraday)']}
                                    />
                                </tbody>
                            </Table>
                        </div>
                    </Col>
                </Row>
            </Container>
        );
    }

}

export default BondFuturesMonitor;
