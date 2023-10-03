import React from 'react';

import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/Row';
import Tab from 'react-bootstrap/Tab';
import Table from 'react-bootstrap/Table';

import TreasuriesMonitor from './treasuries_monitor_container';
import FuturesTable from './futures_table';

const upColor = '#198754';  // green
const downColor = '#dc3545';  // red
const unchColor = '#bdbdbd'; // default text color
const bbgColor = '#ff6600'; // orange

const benchmarkTsys = [
    'US 1M',
    'US 2M',
    'US 3M',
    'US 4M',
    'US 6M',
    'US 1Y',
    'US 2Y',
    'US 3Y',
    'US 5Y',
    'US 7Y',
    'US 10Y',
    'US 20Y',
    'US 30Y'
];

const benchmarkTips = [
    'TIPS 5Y',
    'TIPS 10Y',
    'TIPS 30Y'
];

const cnbcLogo = "https://upload.wikimedia.org/wikipedia/commons/e/e3/CNBC_logo.svg";
const wsjLogo = "https://www.redledges.com/wp-content/uploads/2021/09/WSJ-logo-black.jpeg";
const mwLogo = "https://www.saashub.com/images/app/service_logos/19/47ac30a4ded4/medium.png?1542368413";
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
        // Reference data table
        const loading_data_table = <center>{'... Loading data ...'}</center>;
        
        // Tsys benchmark table
        let tsy_data_table = loading_data_table;
        const tsy_table_rows = benchmarkTsys.map(standardName =>
            <tr key={standardName}>
                <td style={{ 
                    textAlign: 'center',
                    color: bbgColor
                }}>{standardName}</td>
                <td style={{ 
                    textAlign: 'center',
                    color: bbgColor
                }}>{(standardName in this.props.referenceData.tsys.otr) ? this.props.referenceData.tsys.otr[standardName].maturityDate : ''}</td> 
                <td style={{ 
                    textAlign: 'center',
                    color: bbgColor
                }}>{(standardName in this.props.referenceData.tsys.otr) ? this.props.referenceData.tsys.otr[standardName].coupon.toFixed(3) + '%' : ''}</td> 
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.quotes.daily.tsys.otr.cnbc, standardName, 'yieldChange')
                }}>{(standardName in this.props.quotes.daily.tsys.otr.cnbc) ? this.props.quotes.daily.tsys.otr.cnbc[standardName].yield.toFixed(3): ''}</td>                
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.quotes.daily.tsys.otr.wsj, standardName, 'yieldChange')
                }}>{(standardName in this.props.quotes.daily.tsys.otr.wsj) ? this.props.quotes.daily.tsys.otr.wsj[standardName].yield.toFixed(3) : ''}</td>
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.quotes.daily.tsys.otr.mw, standardName, 'yieldChange')
                }}>{(standardName in this.props.quotes.daily.tsys.otr.mw) ? this.props.quotes.daily.tsys.otr.mw[standardName].yield.toFixed(3) : ''}</td>
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.quotes.daily.tsys.otr.cnbc, standardName, 'priceChange')
                }}>{(standardName in this.props.quotes.daily.tsys.otr.cnbc) ? this.props.quotes.daily.tsys.otr.cnbc[standardName].price.toFixed(3) : ''}</td>   
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.quotes.daily.tsys.otr.wsj, standardName, 'priceChange')
                }}>{(standardName in this.props.quotes.daily.tsys.otr.wsj) ? this.props.quotes.daily.tsys.otr.wsj[standardName].price.toFixed(3) : ''}</td>
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.quotes.daily.tsys.otr.mw, standardName, 'priceChange')
                }}>{(standardName in this.props.quotes.daily.tsys.otr.mw) ? this.props.quotes.daily.tsys.otr.mw[standardName].price.toFixed(3) : ''}</td>
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.quotes.daily.tsys.otr.cme, standardName, 'priceChange')
                }}>{(standardName in this.props.quotes.daily.tsys.otr.cme) ? this.props.quotes.daily.tsys.otr.cme[standardName].price.toFixed(3) : ''}</td>           
                <td style={{ textAlign: 'center' }}>{(standardName in this.props.quotes.daily.tsys.otr.cnbc) ? this.props.quotes.daily.tsys.otr.cnbc[standardName].timestamp.toLocaleTimeString() : ''}</td>                               
            </tr>
        );


    tsy_data_table = <div
            style={{ height: '500px', overflow: 'auto' }}
        >
        <Table
            id="tsys-benchmark-table"
            responsive
            hover
        >
            <thead>
                <tr style={{ color: unchColor }}>
                    <th style={{ textAlign: 'center' }}>Name</th>
                    <th style={{ textAlign: 'center' }}>Maturity</th>
                    <th style={{ textAlign: 'center' }}>Coupon</th>
                    <th style={{ textAlign: 'center' }}>YTM
                        <img src={cnbcLogo} width="36" height="24"></img>
                    </th>
                    <th style={{ textAlign: 'center' }}>YTM
                        <img src={wsjLogo} width="42" height="28"></img>
                    </th>
                    <th style={{ textAlign: 'center' }}>YTM
                        <img src={mwLogo} width="30" height="30"></img>
                    </th>
                    <th style={{ textAlign: 'center' }}>Price
                        <img src={cnbcLogo} width="36" height="24"></img>
                    </th>
                    <th style={{ textAlign: 'center' }}>Price
                        <img src={wsjLogo} width="42" height="28"></img>
                    </th>
                    <th style={{ textAlign: 'center' }}>Price
                        <img src={mwLogo} width="30" height="30"></img>
                    </th>
                    <th style={{ textAlign: 'center' }}>Price
                        <img src={cmeLogo} width="30" height="30"></img>
                    </th>
                    <th style={{ textAlign: 'center' }}>Timestamp</th>
                </tr>
            </thead>
            <tbody
                style={{ color: unchColor }}
            >
                {tsy_table_rows}
            </tbody>
        </Table>
        </div>;

        // TIPS benchmark table
        let tips_data_table = loading_data_table;
        const tips_table_rows = benchmarkTips.map(standardName =>
            <tr key={standardName}>
                <td style={{ 
                    textAlign: 'center',
                    color: bbgColor }}>{standardName}</td>
                <td style={{ 
                    textAlign: 'center',
                    color: bbgColor }}>{(standardName in this.props.referenceData.tips.otr) ? this.props.referenceData.tips.otr[standardName].maturityDate : ''}</td>
                <td style={{ 
                    textAlign: 'center',
                    color: bbgColor }}>{(standardName in this.props.referenceData.tips.otr) ? this.props.referenceData.tips.otr[standardName].coupon.toFixed(3) + '%' : ''}</td>
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
            style={{ height: '200px', width: '600px', overflow: 'auto' }}
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
                            <img src={cnbcLogo} width="36" height="24"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>Price
                            <img src={cnbcLogo} width="36" height="24"></img>
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

                                    <Tab.Pane eventKey="#/market_data/old">
                                        <Row>
                                            {/* Tsys benchmark table */}
                                            <h2>Treasuries</h2>
                                            {tsy_data_table}
                                        </Row>
                                        <Row
                                            style={{ paddingTop: '25px' }}
                                        >
                                            <Col>
                                                {/* Tips benchmark table */}
                                                <h2>TIPS</h2>
                                                {tips_data_table}
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