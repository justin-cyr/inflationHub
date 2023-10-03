import React from 'react';

import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/Row';
import Tab from 'react-bootstrap/Tab';
import Table from 'react-bootstrap/Table';

import TreasuriesMonitor from './treasuries_monitor_container';
import BondFuturesMonitor from './bond_futures_monitor_container';
import FuturesTable from './futures_table';

const upColor = '#198754';  // green
const downColor = '#dc3545';  // red
const unchColor = '#bdbdbd'; // default text color

const cmeLogo = "https://ffnews.com/wp-content/uploads/2022/03/1625171625444.jpg";

class MarketData extends React.Component {

    constructor(props) {
        super(props);

        this.getChangeColor = this.getChangeColor.bind(this);
    }
    
    getChangeColor(quoteObj, key, field) {
        if ((key in quoteObj) && (field in quoteObj[key])) {
            if (quoteObj[key][field] > 0) {
                return upColor;
            }
            else if (quoteObj[key][field] < 0) {
                return downColor;
            }
        }
        return unchColor;
    }

    render() {

        const bond_futures_table_heading = (
            <tr style={{ color: unchColor }}>
                <th style={{ textAlign: 'center' }}>Month</th>
                <th style={{ textAlign: 'center' }}>Ticker</th>
                <th style={{ textAlign: 'center' }}>Price
                    <img src={cmeLogo} width="30" height="30"></img>
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
                    <Tab.Container id="market-data-tabs" defaultActiveKey="#/market_data/treasuries_monitor">
                        <Row>
                            <Col
                                md="auto"
                            >
                                <ListGroup>
                                    <ListGroup.Item action href="#/market_data/treasuries_monitor">Treasuries Monitor</ListGroup.Item>
                                    <ListGroup.Item action href="#/market_data/bond_futures_monitor">Bond Futures Monitor</ListGroup.Item>
                                    <ListGroup.Item action href="#/market_data/old">Old page</ListGroup.Item>
                                </ListGroup>
                            </Col>
                            <Col
                                style={{ textAlign: "center" }}
                            >
                                <Tab.Content>

                                    <Tab.Pane eventKey="#/market_data/treasuries_monitor">
                                        <h3>{'Treasuries Monitor'}</h3>
                                        <TreasuriesMonitor getChangeColor={this.getChangeColor} />
                                    </Tab.Pane>

                                    <Tab.Pane eventKey="#/market_data/bond_futures_monitor">
                                        <h3>{'Bond Futures Monitor'}</h3>
                                        <BondFuturesMonitor getChangeColor={this.getChangeColor} />
                                    </Tab.Pane>

                                    <Tab.Pane eventKey="#/market_data/old">
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
                                    </Tab.Pane>

                                </Tab.Content>
                            </Col>
                        </Row>
                    </Tab.Container>
                </Row>
            </Container>
        );
    }
  }

export default MarketData;