import React from 'react';

import Table from 'react-bootstrap/Table';

const unchColor = '#bdbdbd'; // default text color
const bbgColor = '#ff6600'; // orange

class EtfTable extends React.Component {
    constructor(props) {
        super(props);

        /* expect these props:
            etfs: (Object) { ticker: description }
            data: (Object) { ticker: {price, change, changePercent, time, ... } }
            id: (string)
            height: (string)
            width: (string)
            getChangeColor: function
            logo: (string)
        */

        this.getChangeColor = this.props.getChangeColor;
    }

    render() {
        const loading_data_table = <center>{'... Loading data ...'}</center>;
        let etf_data_table = loading_data_table;
        const etf_table_rows = Object.keys(this.props.etfs).map(ticker =>
            <tr key={ticker}>
                <td style={{
                    textAlign: 'center',
                    color: bbgColor
                }}>{ticker}</td>
                <td style={{
                    textAlign: 'center',
                    color: bbgColor
                }}>{this.props.etfs[ticker]}</td>
                <td style={{
                    textAlign: 'center',
                    color: unchColor
                }}>{(ticker in this.props.data) ? this.props.data[ticker].price.toFixed(3) : ''}</td>
                <td style={{
                    textAlign: 'center',
                    color: this.getChangeColor(this.props.data, ticker, 'changePercent')
                }}>{(ticker in this.props.data) ? this.props.data[ticker].changePercent.toFixed(3) + '% (' + this.props.data[ticker].change.toFixed(3) + ')' : ''}</td>
                <td style={{
                    textAlign: 'center',
                    color: unchColor
                }}>{(ticker in this.props.data) ? this.props.data[ticker].dayVolume : ''}</td>
                <td style={{ textAlign: 'center' }}>{(ticker in this.props.data) ? (new Date(this.props.data[ticker].time)).toLocaleTimeString() : ''}</td>
            </tr>
        );

        etf_data_table = <div
            style={{ height: this.props.height, width: this.props.width, overflow: 'auto' }}
        >
            <Table
                id={this.props.id}
                responsive
                hover
            >
                <thead>
                    <tr style={{ color: unchColor }}>
                        <th style={{ textAlign: 'center' }}>Ticker</th>
                        <th style={{ textAlign: 'center' }}>Description</th>
                        <th style={{ textAlign: 'center' }}>Price
                            <img src={this.props.logo} width="36" height="24"></img>
                        </th>
                        <th style={{ textAlign: 'center' }}>Change</th>
                        <th style={{ textAlign: 'center' }}>Volume</th>
                        <th style={{ textAlign: 'center' }}>Timestamp</th>
                    </tr>
                </thead>
                <tbody
                    style={{ color: unchColor }}
                >
                    {etf_table_rows}
                </tbody>
            </Table>
        </div>;

        return etf_data_table;
    }

}

export default EtfTable;
