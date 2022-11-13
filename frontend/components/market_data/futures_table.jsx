import React from 'react';

import Table from 'react-bootstrap/Table';

class FuturesTable extends React.Component {
    constructor(props) {
        super(props);

        /* expect these props:
            title: (string) name of the data
            data: (Object) { ticker: { ticker, month, last, price, priorSettle, priceChange, productName, volume, expirationDate, timestamp }}
            sourceLogo: (string) link to source logo
            upColor: (string) color for increase
            downColor: (string) color for decrease
            unchColor: (string) color for unchanged
            bbgColor: (string) color for static fields
            height: (string) componet height in px
            logoWidth: (string) logo width in px
            logoHeight: (string) logo height in px
        */
    }

    getChangeColor(quoteObj, key, field) {
        if ((key in quoteObj) && (field in quoteObj[key])) {
            if (quoteObj[key][field] > 0) {
                return this.props.upColor;
            }
            else if (quoteObj[key][field] < 0) {
                return this.props.downColor;
            }
        }
        return this.props.unchColor;
    }

    render() {
        const loading_data_table = <center>{'... Loading data ...'}</center>;
        let data_table = loading_data_table;

        if (this.props.data) {
            let data = Object.values(this.props.data);
            data.sort((a, b) => Number(a.expirationDate) - Number(b.expirationDate));

            const table_rows = data.map(record =>
                <tr key={record.ticker}>
                    <td style={{
                        textAlign: 'center',
                        color: this.props.bbgColor
                    }}>{record.productName}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.props.bbgColor
                    }}>{record.month}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.props.bbgColor
                    }}>{record.ticker}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.getChangeColor(this.props.data, record.ticker, 'priceChange')
                    }}>{record.price}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.getChangeColor(this.props.data, record.ticker, 'priceChange')
                    }}>{record.last}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.props.unchColor
                    }}>{record.priorSettle}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.props.unchColor
                    }}>{record.volume}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.props.unchColor
                    }}>{record.timestamp.toLocaleTimeString()}</td>
                </tr>
            );

            const table_heading = (
                <tr style={{ color: this.props.unchColor }}>
                    <th style={{ textAlign: 'center' }}>Name</th>
                    <th style={{ textAlign: 'center' }}>Month</th>
                    <th style={{ textAlign: 'center' }}>Ticker</th>
                    <th style={{ textAlign: 'center' }}>Price
                        <img src={this.props.sourceLogo} width={this.props.logoWidth || 30} height={this.props.logoHeight || 30}></img>
                    </th>
                    <th style={{ textAlign: 'center' }}>Last</th>
                    <th style={{ textAlign: 'center' }}>Prior Settle</th>
                    <th style={{ textAlign: 'center' }}>Volume</th>
                    <th style={{ textAlign: 'center' }}>Timestamp</th>
                </tr>
            );

            data_table = (
                <Table
                    id={this.props.title}
                    responsive
                    hover
                >
                    <thead>
                        {table_heading}
                    </thead>
                    <tbody
                        style={{ color: this.props.unchColor }}
                    >
                        {table_rows}
                    </tbody>
                </Table>
            );
        }
        

        return (<div
            style={{ height: this.props.height, width: '1100px', overflow: 'auto' }}
        >
            {data_table}
        </div>
        );

    }
}

export default FuturesTable;
