import React from 'react';
import $, { merge } from 'jquery';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';


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

        this.getTreasuryYieldfromWSJ = this.getTreasuryYieldfromWSJ.bind(this);
    }

    getTreasuryYieldfromWSJ() {
        // Request Market price data
        $.ajax({
            url: '/data/WSJ US Treasury Yields (intraday)',
            method: 'GET',

            complete: () => {
                // schedule the next request only when the current one is complete
                if (this._isMounted) {
                    console.log('Schdule the next');
                    setTimeout(this.getTreasuryYieldfromWSJ, 10000);
                }
            },


            success: (response) => {
                const wsjTreasuryYields = response.data;
                console.log(response);


                this._isMounted && this.setState({
                    wsjTreasuryYields: wsjTreasuryYields
                });
            }


        });
    }
    
    componentDidMount() {
        this._isMounted = true;
        this.getTreasuryYieldfromWSJ();
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    render() {
        // Reference data table
        let data_table = <center>{'... Loading data ...'}</center>;
        
        // if wsjTreasuryYields(dict) is defined
        if (this.state.wsjTreasuryYields) {
            const table_rows = this.state.wsjTreasuryYields.length === 0
                ? <tr key={'empty'}><td colSpan="7"><center>{'... Loading data ...'}</center></td></tr>
                : this.state.wsjTreasuryYields.map(record => 
                    <tr key={record['name']}>
                        <td style={{ textAlign: 'center' }}>{record['name']}</td> 
                        <td style={{ textAlign: 'center' }}>{Number(record['coupon']).toFixed(3) + '%'}</td> 
                        <td style={{ textAlign: 'center',
                                     color: record['priceChange'][0] === '-' ? this.state.downColor : this.state.upColor  
                                                         }}>{Number(record['price']).toFixed(3)}</td>    
                        <td style={{ textAlign: 'center' }}>{record['priceChange']}</td>                
                        <td style={{ textAlign: 'center' }}>{record['yield']}</td>        
                        <td style={{ textAlign: 'center' }}>{record['yieldChange']}</td>  
                        <td style={{ textAlign: 'center' }}>{record['timestamp']}</td>                               
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
                        <th style={{ textAlign: 'center' }}>Coupon</th>
                        <th style={{ textAlign: 'center' }}>Price</th>
                        <th style={{ textAlign: 'center' }}>Price Change</th>
                        <th style={{ textAlign: 'center' }}>YTM</th>
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
        }
        // if we do not comment off the following line, the table will auto update secondly 
        //this.getTreasuryYieldfromWSJ();
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