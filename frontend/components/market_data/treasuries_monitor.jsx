import React from 'react';

import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';

const unchColor = '#bdbdbd'; // default text color
const bbgColor = '#ff6600'; // orange

class TreasuriesMonitor extends React.Component {
    constructor(props) {
        super(props);

        this.getChangeColor = this.props.getChangeColor;
    }

    render() {
        // Reference data table
        const loading_data_table = <center>{'... Loading data ...'}</center>;

        // Tsys benchmark table
        let tsy_data_table = loading_data_table;
        const tsy_table_rows = this.props.referenceData.tsys.benchmarkTsys.map(standardName =>
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
                }}>{(standardName in this.props.quotes.daily.tsys.otr.cnbc) ? this.props.quotes.daily.tsys.otr.cnbc[standardName].yield.toFixed(3) : ''}</td>
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
            style={{ height: '600px', overflow: 'auto' }}
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
                            <img src={this.props.referenceData.logos.cnbc} width="36" height="24"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>YTM
                            <img src={this.props.referenceData.logos.wsj} width="42" height="28"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>YTM
                            <img src={this.props.referenceData.logos.mw} width="30" height="30"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>Price
                            <img src={this.props.referenceData.logos.cnbc} width="36" height="24"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>Price
                            <img src={this.props.referenceData.logos.wsj} width="42" height="28"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>Price
                            <img src={this.props.referenceData.logos.mw} width="30" height="30"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>Price
                            <img src={this.props.referenceData.logos.cme} width="30" height="30"></img>
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

        return (
            <Container fluid>
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
            </Container>
        );
    }
}

export default TreasuriesMonitor;