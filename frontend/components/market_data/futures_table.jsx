import React from 'react';

import Table from 'react-bootstrap/Table';

const upColor = '#198754';  // green
const downColor = '#dc3545';  // red
const unchColor = '#bdbdbd'; // default text color
const bbgColor = '#ff6600'; // orange

class FuturesTable extends React.Component {
    constructor(props) {
        super(props);

        /* expect these props:
            title: (string) name of the data
            data: (Object) { ticker: { ticker, month, last, price, priorSettle, priceChange, productName, volume, expirationDate, timestamp }}
            upColor: (string) color for increase
            downColor: (string) color for decrease
            unchColor: (string) color for unchanged
            bbgColor: (string) color for static fields
        */

        this.state = {
            upColor: this.props.upColor || upColor,
            downColor: this.props.downColor || downColor,
            unchColor: this.props.unchColor || unchColor,
            bbgColor: this.props.bbgColor || bbgColor
        }

    }

    getChangeColor(quoteObj, key, field) {
        if ((key in quoteObj) && (field in quoteObj[key])) {
            if (quoteObj[key][field] > 0) {
                return this.state.upColor;
            }
            else if (quoteObj[key][field] < 0) {
                return this.state.downColor;
            }
        }
        return this.state.unchColor;
    }

    render() {
        let table_rows = [<tr key={this.props.title} style={{ color: this.state.unchColor }}>
            <td colSpan="7" style={{
                textAlign: 'center',
                color: 'yellowgreen'
            }}>{this.props.title}</td>
            </tr>];

        if (this.props.data) {
            let data = Object.values(this.props.data);
            data.sort((a, b) => Number(a.expirationDate) - Number(b.expirationDate));

            table_rows = table_rows.concat(data.map(record =>
                <tr key={record.ticker}>
                    <td style={{
                        textAlign: 'center',
                        color: this.state.bbgColor
                    }}>{record.month}</td>
                    <td style={{
                        textAlign: 'center',
                        color: this.state.bbgColor
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
                        textAlign: 'center'
                    }}>{record.priorSettle}</td>
                    <td style={{
                        textAlign: 'center'
                    }}>{record.volume}</td>
                    <td style={{
                        textAlign: 'center'
                    }}>{record.timestamp.toLocaleTimeString()}</td>
                </tr>
            ));
        }

        return table_rows;

    }
}

export default FuturesTable;
