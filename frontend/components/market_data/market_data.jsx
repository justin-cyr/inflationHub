import React from 'react';
import $, { merge } from 'jquery';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';

const benchmarkTsys = [
    'US 1M',
    'US 3M',
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

class MarketData extends React.Component {

    constructor(props) {
        super(props);

        const today = new Date();
        const year = today.getFullYear().toString();
        const month = (1 + today.getMonth()).toString().padStart(2, '0');
        const day = today.getDate().toString().padStart(2, '0');
        const todayStr = year + '-' + month + '-' + day;

        this._isMounted = false;
        this.state = {
            wsjTreasuryYields: [],
            // styles
            upColor:    '#198754',  // green
            downColor:  '#dc3545',  // red
        }

    }
    
    componentDidMount() {
        this._isMounted = true;
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    render() {
        // Reference data table
        let data_table = <center>{'... Loading data ...'}</center>;
        
        // if quotes have updated in the state

        const table_rows = benchmarkTsys.map(standardName =>
            <tr key={standardName}>
                <td style={{ textAlign: 'center' }}>{standardName}</td>
                <td style={{ textAlign: 'center' }}>{(standardName in this.props.referenceData.tsys.otr) ? this.props.referenceData.tsys.otr[standardName].maturityDate : ''}</td> 
                <td style={{ textAlign: 'center' }}>{(standardName in this.props.referenceData.tsys.otr) ? this.props.referenceData.tsys.otr[standardName].coupon.toFixed(3) + '%' : ''}</td> 
                <td style={{ textAlign: 'center',
                color: (standardName in this.props.quotes.daily.tsys.otr.wsj) 
                        && this.props.quotes.daily.tsys.otr.wsj[standardName].priceChange[0] === '-'
                        ? this.state.downColor
                        : this.state.upColor  
                }}>{(standardName in this.props.quotes.daily.tsys.otr.wsj) ? this.props.quotes.daily.tsys.otr.wsj[standardName].price.toFixed(3) : ''}</td>    
                <td style={{ textAlign: 'center' }}>{(standardName in this.props.quotes.daily.tsys.otr.cnbc) ? this.props.quotes.daily.tsys.otr.cnbc[standardName].yield.toFixed(3): ''}</td>                
                <td style={{ textAlign: 'center' }}>{(standardName in this.props.quotes.daily.tsys.otr.wsj) ? this.props.quotes.daily.tsys.otr.wsj[standardName].yield.toFixed(3) : ''}</td>          
                <td style={{ textAlign: 'center' }}>{(standardName in this.props.quotes.daily.tsys.otr.wsj) ? this.props.quotes.daily.tsys.otr.wsj[standardName].yieldChange : ''}</td>  
                <td style={{ textAlign: 'center' }}>{(standardName in this.props.quotes.daily.tsys.otr.cnbc) ? this.props.quotes.daily.tsys.otr.cnbc[standardName].timestamp.toLocaleTimeString() : ''}</td>                               
            </tr>
        );


    data_table = <div
            style={{ height: '500px', overflow: 'auto' }}
        >
        <Table
            id="market-data-table"
            responsive
            hover
        >
            <thead>
                <tr style={{ color: '#bdbdbd'}}>
                    <th style={{ textAlign: 'center' }}>Name</th>
                    <th style={{ textAlign: 'center' }}>Maturity</th>
                    <th style={{ textAlign: 'center' }}>Coupon</th>
                    <th style={{ textAlign: 'center' }}>Price</th>
                    <th style={{ textAlign: 'center' }}>YTM
                        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/CNBC_logo.svg" width="36" height="24"></img>
                        </th>
                    <th style={{ textAlign: 'center' }}>YTM
                        <img src="https://www.redledges.com/wp-content/uploads/2021/09/WSJ-logo-black.jpeg" width="42" height="28"></img>
                        </th>
                    <th style={{ textAlign: 'center' }}>YTM Change</th>
                    <th style={{ textAlign: 'center' }}>Timestamp</th>
                </tr>
            </thead>
            <tbody
                style={{ color: '#bdbdbd' }}
            >
                {table_rows}
            </tbody>
        </Table>
        </div>;


        return (
            <Container fluid>
                <Row>
                    {/* Table */}
                    {data_table}
                </Row>
            </Container>
        );
    }
  }

export default MarketData;