import React from 'react';
import $ from 'jquery';

import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';

class TipsData extends React.Component {
    
    constructor(props) {
        super(props);

        this.state = {
            referenceData: []
        }

        // bind methods
        this.getTipsData = this.getTipsData.bind(this);
    }

    getTipsData() {
        // Request TIPS reference data
        $.ajax({
            url: '/tips_reference_data',
            method: 'GET',
            success: (response) => {
                console.log(response.referenceData);

                this.setState({
                    referenceData: response.referenceData
                });
            }
        });
    }

    componentDidMount() {
        this.getTipsData();
    }

    render() {

        let data_table = <center>{'... Loading data ...'}</center>;
        if (this.state.referenceData) {

            const table_rows = this.state.referenceData.length === 0
                ? <tr key={'empty'}><td colSpan="7"><center>{'... Loading data ...'}</center></td></tr>
                : this.state.referenceData.map(record => 
                    <tr key={record['cusip']}>
                        <td style={{ textAlign: 'center' }}>{record['cusip']}</td>
                        <td style={{ textAlign: 'left' }}>{Number(record['interestRate']).toFixed(3) +'%'}</td>
                        <td style={{ textAlign: 'left' }}>{record['maturityDate']}</td>
                        <td style={{ textAlign: 'left' }}>{record['tenor'].toFixed(2) + "Y"}</td>
                        <td style={{ textAlign: 'left' }}>{record['issueDate']}</td>
                        <td style={{ textAlign: 'left' }}>{record['datedDate']}</td>
                        <td style={{ textAlign: 'center' }}>{Number(record['refCpiOnDatedDate']).toFixed(5)}</td>
                        <td style={{ textAlign: 'left' }}>{record['securityTerm']}</td>
                        <td style={{ textAlign: 'left' }}>{record['series']}</td>
                    </tr>    
                );

            data_table = <Table
                id="tips-data-table"
                responsive="true"
            >
                <thead>
                    <tr style={{ color: '#bdbdbd'}}>
                        <th style={{ textAlign: 'center' }}>CUSIP</th>
                        <th style={{ textAlign: 'left' }}>Coupon</th>
                        <th style={{ textAlign: 'left' }}>Maturity Date</th>
                        <th style={{ textAlign: 'left' }}>Tenor</th>
                        <th style={{ textAlign: 'left' }}>Issue Date</th>
                        <th style={{ textAlign: 'left' }}>Dated Date</th>
                        <th style={{ textAlign: 'center' }}>Ref CPI on Dated Date</th>
                        <th style={{ textAlign: 'left' }}>Security Term</th>
                        <th style={{ textAlign: 'left' }}>Series</th>
                    </tr>
                </thead>
                <tbody
                    style={{ color: '#bdbdbd' }}
                >
                    {table_rows}
                </tbody>
            </Table>;
        }

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

export default TipsData;
