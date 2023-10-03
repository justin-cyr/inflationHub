import React from 'react';

import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';

import FuturesTable from './futures_table';

const unchColor = '#bdbdbd'; // default text color
const oneMonthTableWith = '650px';

class IRFuturesMonitor extends React.Component {
    constructor(props) {
        super(props);

        this.getChangeColor = this.props.getChangeColor;
    }

    render() {
        const futures_table_heading = (
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
                        <div
                            style={{ height: this.props.height, width: oneMonthTableWith, overflow: 'auto' }}
                        >
                            <Table
                                id="ff-futures-table"
                                responsive
                                hover
                                style={{ color: unchColor }}
                            >
                                <thead>
                                    {futures_table_heading}
                                </thead>
                                <tbody>
                                    <FuturesTable
                                        title="1M FF Futures"
                                        data={this.props.quotes.daily.futures['CME 30D FF Futures (intraday)']}
                                        filterFutures={true}
                                    />
                                </tbody>
                            </Table>
                        </div>
                    </Col>
                    <Col>
                        <div
                            style={{ height: this.props.height, width: oneMonthTableWith, overflow: 'auto' }}
                        >
                            <Table
                                id="ser-futures-table"
                                responsive
                                hover
                                style={{ color: unchColor }}
                            >
                                <thead>
                                    {futures_table_heading}
                                </thead>
                                <tbody>
                                    <FuturesTable
                                        title="1M SOFR Futures"
                                        data={this.props.quotes.daily.futures['CME 1M SOFR Futures (intraday)']}
                                    />
                                </tbody>
                            </Table>
                        </div>
                    </Col>
                    <Col>
                        <div
                            style={{ height: this.props.height, width: oneMonthTableWith, overflow: 'auto' }}
                        >
                            <Table
                                id="sfr-futures-table"
                                responsive
                                hover
                                style={{ color: unchColor }}
                            >
                                <thead>
                                    {futures_table_heading}
                                </thead>
                                <tbody>
                                    <FuturesTable
                                        title="3M SOFR Futures"
                                        data={this.props.quotes.daily.futures['CME 3M SOFR Futures (intraday)']}
                                        filterFutures={true}
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

export default IRFuturesMonitor;
